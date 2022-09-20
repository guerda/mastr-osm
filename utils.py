import re


class WattFormatter:
    def format(watt: float):
        if watt >= 1000000000:
            factor = 1000000000
            suffix = "GW"
        elif watt >= 1000000:
            factor = 1000000
            suffix = "MW"
        elif watt > 1000:
            factor = 1000
            suffix = "kW"
        else:
            factor = 1
            suffix = "W"

        return ("%.2f %s" % (watt / factor, suffix)).strip()


class PowerParser:
    def parse(power_text: str):
        """
        Accepts a text of the tag `generator:output:electricity` and tries
        to parses it into watts.
        """
        if "yes" == power_text or "" == power_text:
            return 0

        # GW
        # MW
        # kW
        # only number

        g_match = re.search("((\d*(.)?)\d+) GW(p)?", power_text)
        m_match = re.search("((\d*(.)?)\d+) MW(p)?", power_text)
        k_match = re.search("((\d*(.)?)\d+) kW(p)?", power_text)
        w_match = re.search("((\d*(.)?)\d+) W(p)?", power_text)

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
        else:
            try:
                value = float(power_text)
            except ValueError:
                value = 0
            power = 1

        return power * value


if __name__ == "__main__":
    print(WattFormatter.format(3))
    print(WattFormatter.format(3433))
    print(WattFormatter.format(3324000))
    print(WattFormatter.format(33240000000))

    print(PowerParser.parse("18 GWp"))
    print(PowerParser.parse("18 kWp"))
    print(PowerParser.parse("18 MWp"))
    print(PowerParser.parse("18 Wp"))
    print(PowerParser.parse("18 GW"))
    print(PowerParser.parse("18 kW"))
    print(PowerParser.parse("18 MW"))
    print(PowerParser.parse("18 W"))
