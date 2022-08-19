import requests
from zeep import Client
import os
import logging
from rich.logging import RichHandler
import sys
import zeepdatefix 


def get_solar_generators(post_code):
    result = service.GetGefilterteListeStromErzeuger(
        apiKey=api_key, postleitzahl=post_code, marktakteurMastrNummer=mastr_nr, limit=ITEM_CALL_LIMIT
    )
    log.info("Return code: %s" % result["Ergebniscode"])
    log.info("Got %d generators on this call" % len(result["Einheiten"]))
    solar_generators = []
    for anlage in result["Einheiten"]:
        if "Solareinheit" == anlage['Einheittyp']:
            solar_generators.append(anlage)
    return solar_generators

# Prepare logging
ITEM_CALL_LIMIT = 100000
FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger('mastrclient')

# Check if MaStR API key and MaStR number are provided
api_key = os.getenv("API_KEY")
if not api_key:
    log.error('Missing API key, please provide via environment variable API_KEY.')
    sys.exit(1)
mastr_nr = os.getenv("MASTR_NR")
if not api_key:
    log.error('Missing Marktstammdaten Nummer, please provide via environment variable MASTR_NR.')
    sys.exit(1)
log.info("Beginning of API Key: " + api_key[:50])
log.info("MaStR nummer: " + mastr_nr)

# Create MaStR API client
log.info("Create and test MaStR API client...")
client = Client("https://www.marktstammdatenregister.de/MaStRAPI/wsdl/mastr.wsdl")
# Select Anlage12 as port
service = client.bind(service_name="Marktstammdatenregister", port_name="Anlage12")

# Test API connection with time function
log.info("Test API connection")
with client.settings(strict=False):
    response = client.service.GetLokaleUhrzeitMitAuthentifizierung(apiKey=api_key)
    if response['Ergebniscode'] != 'OK':
        raise ValueError('Could not query local time with authentication', response)

    post_code = 40667

    log.info("Retrieve generators filtered by postcode %s" % post_code)
    solar_generators = get_solar_generators(post_code=post_code)

    log.info("%d solar generators in %d " % (len(solar_generators), post_code))
            
    # TODO further pages
    # GetAnlageEegSolar
    # GetGefilterteListeStromErzeuger
