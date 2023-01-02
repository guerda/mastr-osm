import logging
import os
import re
import requests
import sys
import zeepdatefix
import zeep
from decimal import Decimal
from rich.logging import RichHandler
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from generator import SolarGenerator
import tempfile
from datetime import datetime
import humanize


class PowerGenerator:
    def __init__(self):
        pass


class MastrClient:
    def __init__(self, api_key: str, mastr_nr: str):
        """Creates a client for Marktstammdatenregister (short MaStR), defined by MaStR
        number and the API key.

        Args:
            api_key (str): API key for MaStR, base64 encoded key
            mastr_nr (str): MaStR number to use the web service, starts with SOM, 12
              numbers following, e.g. SOM000000000001
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info("Create and test MaStR API client...")
        zeepdatefix.inject_date_fix()
        self.ITEM_CALL_LIMIT = 4000  # None  # 10,000,000
        self.api_key = api_key
        self.mastr_nr = mastr_nr
        cache_file = "%s/zeep-cache.db" % tempfile.gettempdir()
        self.log.info("Zeep cache file: %s" % cache_file)
        cache = SqliteCache(path=cache_file, timeout=60 * 60 * 24 * 7)
        transport = Transport(cache=cache)
        self.client = Client(
            "https://www.marktstammdatenregister.de/MaStRAPI/wsdl/mastr.wsdl",
            transport=transport,
        )
        # Select Anlage12 as port
        self.service = self.client.bind(
            service_name="Marktstammdatenregister",
            port_name="Anlage12",
        )
        self.zip_code_city_pattern = re.compile("^\\d{5} [-\\w]{2,}")

    def create_generator(self, generator) -> SolarGenerator:
        """Creates a generator object from a MaStR object.

        Args:
            generator (_type_): _description_

        Returns:
            SolarGenerator: plain object containing information about commercial usage,
              MaStR number, and capacity
        """
        capacity = generator["Bruttoleistung"]
        is_commercial = not self.zip_code_city_pattern.match(generator["Standort"])
        mastr_reference = generator["EinheitMastrNummer"]

        sg = SolarGenerator(
            capacity=capacity,
            is_commercial=is_commercial,
            mastr_reference=mastr_reference,
        )
        start_time = datetime.now()
        detail_url = self.get_mastr_detail_url(mastr_reference)
        stop_time = datetime.now()
        self.log.debug(
            "MaStR detail URL call took %s"
            % humanize.precisedelta(stop_time - start_time)
        )
        sg.mastr_detail_url = detail_url
        return sg

    def get_solar_generators(self, zip_code: str) -> list[SolarGenerator]:
        """Download solar generators for one zip codes

        Args:
            zip_code (str): Zip code describing the municipality where to download
              solar generators for.

        Returns:
            list[SolarGenerator]: List of SolarGenerator for easy analysis
        """
        with self.client.settings():
            try:
                start_time = datetime.now()
                result = self.service.GetGefilterteListeStromErzeuger(
                    apiKey=self.api_key,
                    postleitzahl=zip_code,
                    marktakteurMastrNummer=self.mastr_nr,
                    limit=self.ITEM_CALL_LIMIT,
                )
                stop_time = datetime.now()
                self.log.info(
                    "Search in MaStR API took %s "
                    % humanize.precisedelta(stop_time - start_time)
                )
                self.log.debug("Return code: %s" % result["Ergebniscode"])
                self.log.debug(
                    "Got %d generators from MaStR" % len(result["Einheiten"])
                )
                solar_generators = []
                for generator in result["Einheiten"]:
                    if "Solareinheit" == generator["Einheittyp"]:
                        sg = self.create_generator(generator)
                        solar_generators.append(sg)
                return solar_generators
            except AttributeError:
                self.log.error("Could not retrieve data from MaStR for %s" % zip_code)
                return None
            except zeep.exceptions.Fault:
                self.log.error("Could not retrieve data from MaStR for %s" % zip_code)
                return None

    def get_generator_details(self, mastr_nr: str):
        with self.client.settings(strict=False):
            result = self.service.GetEinheitSolar(
                apiKey=self.api_key,
                einheitMastrNummer=mastr_nr,
                marktakteurMastrNummer=self.mastr_nr,
            )
            self.log.debug(result)
            lat = result["Breitengrad"]
            lon = result["Laengengrad"]
            return lat, lon

    def get_mastr_detail_url(self, mastr_reference: str):
        if len(mastr_reference) != 15:
            return None
        if mastr_reference[:3] != "SEE":
            return None
        number = mastr_reference[3:]
        base_url = (
            "https://www.marktstammdatenregister.de/MaStR/Schnellsuche/"
            "Schnellsuche?praefix=SEE&mastrNummer=%s"
        )

        r = requests.get(base_url % number)
        if r.status_code != 200:
            return None
        detail_url = "https://www.marktstammdatenregister.de%s" % r.json()["url"]
        self.log.debug("Detail URL for %s: %s" % (mastr_reference, detail_url))
        return detail_url

    def test_api_connection(self):
        with self.client.settings():
            response = self.client.service.GetLokaleUhrzeitMitAuthentifizierung(
                apiKey=self.api_key,
            )
            if response["Ergebniscode"] != "OK":
                raise ValueError(
                    "Could not query local time with authentication",
                    response,
                )


if __name__ == "__main__":
    # Prepare logging
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

    mc = MastrClient(api_key=api_key, mastr_nr=mastr_nr)

    # Create MaStR API client

    # Test API connection with time function
    log.info("Test API connection")
    mc.test_api_connection()

    # Download solar generators for one zip code
    zip_code = 40667

    log.info("Retrieve generators filtered by postcode %s" % zip_code)
    # solar_generators = mc.get_solar_generators(zip_code=zip_code)
    solar_generators = []
    generator_count = len(solar_generators)
    if generator_count > 0:
        log.info("%d solar generators in %d " % (generator_count, zip_code))
        # TODO extract function to sum up capacities
        capacity_sum = Decimal()
        commercial_generator_count = 0
        commercial_capacity = 0
        for generator in solar_generators:
            capacity_sum += generator.capacity
            if generator.is_commercial:
                commercial_generator_count += 1
                commercial_capacity += generator.capacity
        log.info("Brutto capacity: %.2f kW" % capacity_sum)
        percentage_commercial = commercial_generator_count / generator_count
        log.info("%.2f %% commercial generators" % percentage_commercial)
        percentage_commercial_cpcity = commercial_capacity / capacity_sum
        log.info("%.2f %% commercial capacity" % percentage_commercial_cpcity)
        # TODO further pages
    log.info("Get detail location of one generator")
    log.info(mc.get_generator_details("SEE967874079474"))
