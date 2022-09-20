from pydantic import BaseModel


class SolarGenerator(BaseModel):
    capacity: int = None
    is_commercial: bool = False
    mastr_reference: str = None

    def __repr__(self):
        return "%s - capacity: %d, is_commercial: %s, mastr_reference: %s" % (
            type(self).__name__,
            self.capacity,
            self.is_commercial,
            self.mastr_reference
        )
