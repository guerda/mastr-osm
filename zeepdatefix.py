# Fix date parsing for dates from this API. See 
# https://github.com/OpenEnergyPlatform/open-MaStR/issues/10#issuecomment-662688464
import isodate
from zeep.xsd.types import builtins as xsd_builtins_types

def parse_date(_, value):
    # stripping nanoseconds 
    if len(value) == 27:
        value = value[:-8]

    # original function
    if len(value) == 10: 
        value += "T00:00:00"
    return isodate.parse_datetime(value)

# Fix date parsing in order to avoid second issue
xsd_builtins_types.DateTime.pythonvalue = parse_date