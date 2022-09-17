class SolarGenerator:
    def __init__(self, capacity=0, is_commercial=False):
        self._capacity = capacity
        self._is_commercial = is_commercial

    def __repr__(self):
        return "%s - capacity: %d, is_commercial: %s" % (
            type(self),
            self._capacity,
            self._is_commercial,
        )

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, capacity):
        self._capacity = capacity

    @property
    def is_commercial(self):
        return self._is_commercial

    @is_commercial.setter
    def is_commercial(self, is_commercial):
        self._is_commercial = is_commercial
