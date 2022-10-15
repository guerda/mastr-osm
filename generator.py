from pydantic import BaseModel


class SolarGenerator(BaseModel):
    capacity: int = None
    is_commercial: bool = False
    mastr_reference: str = None
    osm_id: int = None

    def __repr__(self):
        return (
            "%s - capacity: %d, is commercial: %s, MaStR reference: %s, OSM ID: %d"
            % (
                type(self).__name__,
                self.capacity,
                self.is_commercial,
                self.mastr_reference,
                self.osm_id,
            )
        )
