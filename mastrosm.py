from osmdownloader import OsmDownloader
from mastrclient import MastrClient
import logging
from rich.logging import RichHandler
import os
import sys


def process_zip_code(mastrclient, osmdownloader, zip_code, log):
    log.info("Zip code %s" % zip_code)
    solar_generators = mastrclient.get_solar_generators(zip_code=zip_code)
    count_mastr = len(solar_generators)

    solar_generators_osm = osmdownloader.get_solar_generators(
        zip_code=zip_code
    ).features
    count_osm = len(solar_generators_osm)
    log.info("Got %d generators in OpenStreetMap" % count_osm)
    mapped_quota = count_osm / count_mastr
    log.info(
        "%.2f %% solar generators captured in %s in OSM" % (mapped_quota, zip_code)
    )


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
    process_zip_code(mc, od, 40667, log)
