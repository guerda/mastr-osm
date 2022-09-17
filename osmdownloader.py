from utils import WattFormatter
import overpass
import logging
import re


class OsmDownloader:
    def __init__(self):
        self.api = overpass.API()
        self.log = logging.getLogger("osmdownloader")

    def get_solar_generators(self, zip_code):
        r = self.api.get(
            """
            rel[postal_code=%d];
            map_to_area;
            nw["power"="generator"]["generator:method"="photovoltaic"](area);
            """
            % zip_code,
            verbosity="geom",
        )
        return r

    def parse_power(power_text):
        """
        Accepts a text of the tag `generator:output:electricity` and tries
        to parses it into watts.
        """
        if "yes" == power_text:
            return 0

        # GW
        # MW
        # kW
        # only number

        g_match = re.search("((\d*(.)?)\d+) GW(p)?", power_text)
        m_match = re.search("((\d*(.)?)\d+) MW(p)?", power_text)
        k_match = re.search("((\d*(.)?)\d+) kW(p)?", power_text)
        w_match = re.search("((\d*(.)?)\d+) W(p)?", power_text)

        logging.info(power_text)

        value = 0
        if w_match:
            value = float(w_match.group(1))
            power = 1
        elif k_match:
            value = float(k_match.group(1))
            power = 1000
        elif m_match:
            value = float(m_match.group(1))
            power = 1000000
        elif g_match:
            value = float(g_match.group(1))
            power = 1000000000

        return power * value


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
