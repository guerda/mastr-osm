import logging
import os
import re
import sys
import zeepdatefix
from decimal import Decimal
from rich.logging import RichHandler
from zeep import Client


def get_solar_generators(post_code):
    result = service.GetGefilterteListeStromErzeuger(
        apiKey=api_key,
        postleitzahl=post_code,
        marktakteurMastrNummer=mastr_nr,
        limit=ITEM_CALL_LIMIT,
    )
    log.info("Return code: %s" % result["Ergebniscode"])
    log.info("Got %d generators on this call" % len(result["Einheiten"]))
    solar_generators = []
    for anlage in result["Einheiten"]:
        if "Solareinheit" == anlage["Einheittyp"]:
            solar_generators.append(anlage)
    return solar_generators


# Prepare logging
ITEM_CALL_LIMIT = 100000
FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("mastrclient")

# Check if MaStR API key and MaStR number are provided
api_key = os.getenv("API_KEY")
if not api_key:
    log.error("Missing API key, please provide via environment " "variable API_KEY.")
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

# Create MaStR API client
log.info("Create and test MaStR API client...")
zeepdatefix.inject_date_fix()
client = Client(
    "https://www.marktstammdatenregister.de/MaStRAPI/wsdl/mastr.wsdl",
)
# Select Anlage12 as port
service = client.bind(
    service_name="Marktstammdatenregister",
    port_name="Anlage12",
)

# Test API connection with time function
log.info("Test API connection")
with client.settings(strict=False):
    response = client.service.GetLokaleUhrzeitMitAuthentifizierung(
        apiKey=api_key,
    )
    if response["Ergebniscode"] != "OK":
        raise ValueError(
            "Could not query local time with authentication",
            response,
        )

    post_code = 40667
    #Köttingen 50374

    log.info("Retrieve generators filtered by postcode %s" % post_code)
    solar_generators = get_solar_generators(post_code=post_code)

    generator_count = len(solar_generators)
    log.info("%d solar generators in %d " % (generator_count, post_code))
    capacity_sum = Decimal()
    postcode_city = re.compile("^\d{5} [-\w]{2,}")
    commercial_generator_count = 0
    commercial_capacity = 0
    for generator in solar_generators:
        capacity_sum += generator["Bruttoleistung"]
        if not postcode_city.match(generator["Standort"]):
            commercial_generator_count += 1
            commercial_capacity += generator["Bruttoleistung"]
    log.info("Brutto capacity: %.2f kW" % capacity_sum)
    percentage_commercial = commercial_generator_count / generator_count
    log.info("%.2f %% commercial generators" % percentage_commercial)
    percentage_commercial_capacity = commercial_capacity / capacity_sum
    log.info("%.2f %% commercial capacity" % percentage_commercial_capacity)
    # TODO further pages
