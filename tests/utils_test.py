from utils import PowerParser, WattFormatter


def test_parse_power_gw():
    assert PowerParser.parse("13 GW") == 13000000000


def test_parse_power_mw():
    assert PowerParser.parse("13 MW") == 13000000


def test_parse_power_kw():
    assert PowerParser.parse("13 kW") == 13000


def test_parse_power_w():
    assert PowerParser.parse("13 W") == 13


def test_parse_power_no_unit():
    assert PowerParser.parse("13") == 13


def test_parse_power_yes():
    assert PowerParser.parse("yes") == 0


def test_parse_power_any():
    assert PowerParser.parse("any") == 0


def test_parse_power_none():
    assert PowerParser.parse("") == 0


def test_parse_power_peak():
    assert PowerParser.parse("13 GWp") == PowerParser.parse("13 GW")
    assert PowerParser.parse("13 MWp") == PowerParser.parse("13 MW")
    assert PowerParser.parse("13 kWp") == PowerParser.parse("13 kW")
    assert PowerParser.parse("13 Wp") == PowerParser.parse("13 W")


def test_format_watt_w():
    assert WattFormatter.format(3) == "3.00 W"


def test_format_watt_kw():
    assert WattFormatter.format(3000) == "3.00 kW"


def test_format_watt_mw():
    assert WattFormatter.format(3000000) == "3.00 MW"


def test_format_watt_gw():
    assert WattFormatter.format(3000000000) == "3.00 GW"
