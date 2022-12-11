from pydantic import BaseModel


class SolarGenerator(BaseModel):
    capacity: float = None
    is_commercial: bool = False
    mastr_reference: str = None
    osm_id: int = None
    lat: float = None
    lon: float = None
    mastr_detail_url: str = None

    def __repr__(self):
        return (
            "%s - capacity: %d, is commercial: %s, MaStR reference: %s, OSM ID: %s"
            % (
                type(self).__name__,
                self.capacity,
                self.is_commercial,
                self.mastr_reference,
                self.osm_id,
            )
        )
