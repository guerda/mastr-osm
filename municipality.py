from pydantic import BaseModel
from datetime import datetime


class MunicipalityHistory(BaseModel):
    dates: list[datetime] = []
    solarGenerators: list[int] = []
    solarGeneratorsMapped: list[int] = []
    missingCommercialGenerators: list[str] = []
