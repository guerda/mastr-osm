import json
import logging
import os
import pydantic
import requests
import sys
import time
from datetime import datetime
from functools import partial
from osmdownloader import OsmDownloader
from pydantic.json import pydantic_encoder
from mastrclient import MastrClient
from municipality import MunicipalityHistory
from rich.logging import RichHandler
from generator import SolarGenerator
import humanize


def generator_to_history_info(generator: SolarGenerator):
    result = {}
    result["mastrReference"] = generator.mastr_reference
    result["lat"] = generator.lat
    result["lon"] = generator.lon
    result["capacity"] = generator.capacity
    result["mastrDetailUrl"] = generator.mastr_detail_url
    return result


def process_zip_code(
    zip_code: str, mastrclient: MastrClient, osmdownloader: OsmDownloader, log
):
    """Downloads data from OpenStreetMap and MaStR for one zip code.
    Helper function for main loop.

    Args:
        zip_code (str): Zip code specifying the municipality for which the data should
        be downloaded.
        mastrclient (MastrClient): The instance of MastrClient which has authentication
        set up to download data from MaStR
        osmdownloader (OsmDownloader): The instance of OsmDownloader which has all
        setup to download data from OSM.
        log (_type_): log object to log information about the process

    Returns:
        int, int: count of solar generators in MaStr, count of solar generators in
         OpenStreetMap
    """
    overall_start_time = datetime.now()
    log.info("Downloading zip code %s" % zip_code)
    # MaStR
    log.info("Load data from MaStR...")
    start_time = datetime.now()
    solar_generators = mastrclient.get_solar_generators(zip_code=zip_code)
    stop_time = datetime.now()
    log.info(
        "Retrieving MaStR data took %s" % humanize.precisedelta(stop_time - start_time)
    )
    count_mastr = len(solar_generators)

    # OpenStreetMap
    log.info("Load data from OSM...")
    start_time = datetime.now()
    solar_generators_osm = osmdownloader.get_solar_generators(zip_code=zip_code)
    stop_time = datetime.now()
    log.info(
        "Loading data from OSM took %s " % humanize.precisedelta(stop_time - start_time)
    )
    count_osm = len(solar_generators_osm)

    # Missing commercial generators in OSM
    osm_refs = set([g.mastr_reference for g in solar_generators_osm])

    missing_generators = []
    for g in solar_generators:
        if g.is_commercial and g.mastr_reference not in osm_refs:
            gh = obtain_generator_details(g, mastrclient)
            missing_generators.append(gh)
    log.debug(missing_generators)
    log.debug("Got %d generators in OpenStreetMap" % count_osm)

    # Quota of mapped generators
    mapped_quota = count_osm / count_mastr
    log.debug(
        "%.2f %% solar generators captured in %s in OSM" % (mapped_quota, zip_code)
    )

    overall_stop_time = datetime.now()
    log.info(
        "Overall process for zip code took %s"
        % humanize.precisedelta(overall_stop_time - overall_start_time)
    )
    return count_mastr, count_osm, missing_generators


def obtain_generator_details(g: SolarGenerator, mastrclient: MastrClient):
    # Add location
    lat, lon = mastrclient.get_generator_details(g.mastr_reference)
    g.lat = lat
    g.lon = lon

    gh = generator_to_history_info(g)
    return gh


if __name__ == "__main__":
    level = os.getenv("LOGLEVEL", "INFO")
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    log = logging.getLogger("mastrclient")

    # Check if MaStR API key and MaStR number are provided
    api_key = os.getenv("MASTR_API_KEY")
    if not api_key:
        log.error(
            "Missing MaStR API key, please provide via environment "
            "variable MASTR_API_KEY."
        )
        sys.exit(1)
    mastr_nr = os.getenv("MASTR_NR")
    if not api_key:
        log.error(
            "Missing Marktstammdaten Nummer, please provide via"
            "environment variable MASTR_NR."
        )
        sys.exit(1)
    log.info("Beginning of API Key: " + api_key[:50])
    log.info("MaStR nummer: " + mastr_nr)
    log.info("Creating and testing MaStR client...")
    mc = MastrClient(api_key=api_key, mastr_nr=mastr_nr)
    mc.test_api_connection()

    log.info("Creating OpenStreetMap downloader...")
    od = OsmDownloader()

    log.info("Start downloading data...")
    i = 0
    # Read out all zip codes from the source file
    zip_codes = []
    with open("zip_codes_small.txt", "r") as f:
        for line in f:
            i += 1
            if i == 1:
                continue
            city_arr = line.split(";")
            city = city_arr[0]
            zip_code = city_arr[2]
            zip_codes.append((zip_code, city))
    log.info("Processing %d zip codes..." % len(zip_codes))

    # Download data for each zip code
    partial_func = partial(process_zip_code, mastrclient=mc, osmdownloader=od, log=log)
    for zip_code, city in zip_codes:
        # Load historic data for this municipality
        history_file = "docs/data/%s.json" % zip_code
        m: MunicipalityHistory = MunicipalityHistory()
        if os.path.isfile(history_file):
            try:
                with open(history_file, "r") as f:
                    history_json = json.load(f)
                    m = MunicipalityHistory.model_validate(history_json)
            except pydantic.error_wrappers.ValidationError:
                log.exception("Could not load history file '%s'" % history_file)
        # Skip if data is newer than 24 hours
        if (datetime.now() - m.dates[-1]).days < 1:
            continue

        m.dates.append(datetime.now())
        # Download data from OSM and MaStR
        try:
            (
                solar_generators,
                solar_generators_mapped,
                missing_generators,
            ) = partial_func(zip_code)
            m.solarGenerators.append(solar_generators)
            m.solarGeneratorsMapped.append(solar_generators_mapped)
            m.missingCommercialGenerators = missing_generators
            log.info("MaStR: %s, OSM: %s" % (solar_generators, solar_generators_mapped))
            # Write data to data file
            with open(history_file, "w") as f:
                f.write(json.dumps(m, indent=4, default=pydantic_encoder))
        except requests.exceptions.ConnectionError:
            log.exception("Could not download data for zip code %s" % zip_code)

        waiting_time = 0.5
        log.info(
            "Waiting %.2f seconds in order to not overload the server." % waiting_time
        )
        time.sleep(waiting_time)

    available_zip_codes = []
    for zip_code, city in zip_codes:
        if os.path.isfile("docs/data/%s.json" % zip_code):
            available_zip_codes.append({"zipCode": zip_code, "city": city})

    # Write processed zip codes to file for selection in the UI
    with open("docs/data/available-zip-codes.json", "w") as f:
        f.write(json.dumps(available_zip_codes, indent=4, default=pydantic_encoder))
