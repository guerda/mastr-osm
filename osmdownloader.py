from utils import WattFormatter, PowerParser
import overpass
import logging
from generator import SolarGenerator
import time


class OsmDownloader:
    def __init__(self):
        self.api = overpass.API(timeout=40)
        self.log = logging.getLogger("osmdownloader")

    def get_solar_generators(self, zip_code: str) -> list[SolarGenerator]:
        while self.api.slots_available == 0:
            time.sleep(5)
        r = self.api.get(
            """
            rel[postal_code=%s];
            map_to_area;
            nw["power"="generator"]["generator:method"="photovoltaic"](area);
            """
            % zip_code,
            verbosity="geom",
        )
        logging.debug(r)
        generators = []
        for f in r.features:
            generator = self.create_generator(f)
            generators.append(generator)
            # sum_power += power
        return generators

    def create_generator(self, features) -> SolarGenerator:
        generator = SolarGenerator()
        # Is generator commercial?
        generator.is_commercial = (
            "ref" in features.properties and "operator" in features.properties
        )

        # OSM Node ID
        # if "id" in features.properties:
        #    generator.osm_id = features.properties["id"]

        # Which capacity does the generator have?
        generator.capacity = 0
        if "generator:output:electricity" in features.properties:
            generator.capacity = PowerParser.parse(
                features.properties["generator:output:electricity"]
            )
        if "ref" in features.properties:
            generator.mastr_reference = features.properties["ref"]
        self.log.debug(features.properties)
        return generator


if __name__ == "__main__":
    from rich.logging import RichHandler

    FORMAT = "%(message)s"
    logging.basicConfig(
        level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    od = OsmDownloader()
    generators = od.get_solar_generators(40667)
    logging.info(generators)
    logging.info("%d PV generators" % len(generators))
    sum_power = sum([g.capacity for g in generators])
    count_commercials = len([g for g in generators if g.is_commercial])
    logging.info("Total sum of at least %s watt peak" % WattFormatter.format(sum_power))
    logging.info("%d commercial generators" % count_commercials)
