class WattFormatter:
    def format(watt):
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
            suffix = ""

        return ("%.2f %s" % (watt / factor, suffix)).strip()


if __name__ == "__main__":
    print(WattFormatter.format(3))
    print(WattFormatter.format(3433))
    print(WattFormatter.format(3324000))
    print(WattFormatter.format(33240000000))
