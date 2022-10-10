from osmdownloader import OsmDownloader
from mastrclient import MastrClient
import logging
from rich.logging import RichHandler
import os
import sys
import multiprocessing as mp
from functools import partial


def process_zip_code(zip_code, mastrclient, osmdownloader, log):
    log.info("Downloading zip code %s" % zip_code)
    solar_generators = mastrclient.get_solar_generators(zip_code=zip_code)
    count_mastr = len(solar_generators)

    solar_generators_osm = osmdownloader.get_solar_generators(
        zip_code=zip_code
    ).features
    count_osm = len(solar_generators_osm)
    log.debug("Got %d generators in OpenStreetMap" % count_osm)
    mapped_quota = count_osm / count_mastr
    log.debug(
        "%.2f %% solar generators captured in %s in OSM" % (mapped_quota, zip_code)
    )
    return count_mastr, count_osm


if __name__ == "__main__":
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
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
    zip_codes = []
    with open("zip_codes_small.txt", "r") as f:
        for line in f:
            i += 1
            if i == 1:
                continue
            city_arr = line.split(";")
            city = city_arr[0]
            zip_code = city_arr[2]
            zip_codes.append(zip_code)
    log.info("Processing %d zip codes..." % len(zip_codes))

    log.info("Prepare multiprocessing with %d cores..." % mp.cpu_count())
    partial_func = partial(process_zip_code, mastrclient=mc, osmdownloader=od, log=log)
    for zip_code in zip_codes:
        log.info("MaStR: %s, OSM: %s" % partial_func(zip_code))