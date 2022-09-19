from utils import WattFormatter, PowerParser
import overpass
import logging


class OsmDownloader:
    def __init__(self):
        self.api = overpass.API()
        self.log = logging.getLogger("osmdownloader")

    def get_solar_generators(self, zip_code: str):
        r = self.api.get(
            """
            rel[postal_code=%s];
            map_to_area;
            nw["power"="generator"]["generator:method"="photovoltaic"](area);
            """
            % zip_code,
            verbosity="geom",
        )
        return r

    def parse_power(power_text):
        return PowerParser.parse(power_text)


if __name__ == "__main__":
    from rich.logging import RichHandler

    FORMAT = "%(message)s"
    logging.basicConfig(
        level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    od = OsmDownloader()
    r = od.get_solar_generators(40667)
    logging.debug(r)
    sum_power = 0
    count_commercials = 0
    # TODO extract to function
    for f in r.features:
        is_commercial = "ref" in f.properties and "operator" in f.properties
        if is_commercial:
            count_commercials += 1
        if "generator:output:electricity" in f.properties:
            power = OsmDownloader.parse_power(
                f.properties["generator:output:electricity"]
            )
            sum_power += power
        logging.info(f.properties)
    logging.info("%d PV generators" % len(r.features))
    logging.info("Total sum of at least %d watt peak" % WattFormatter.format(sum_power))
    logging.info("%d commercial generators" % count_commercials)
