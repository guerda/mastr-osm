from pydantic import BaseModel
from datetime import datetime


class CommercialGeneratorInfo(BaseModel):
    mastrReference: str
    lat: float = 0.0
    lon: float = 0.0


class MunicipalityHistory(BaseModel):
    dates: list[datetime] = []
    solarGenerators: list[int] = []
    solarGeneratorsMapped: list[int] = []
    missingCommercialGenerators: list[CommercialGeneratorInfo] = None


class MunicipalityHistoryV1(BaseModel):
    dates: list[datetime] = []
    solarGenerators: list[int] = []
    solarGeneratorsMapped: list[int] = []
    missingCommercialGenerators: list[str] = None

    def convert_to_v2(self):
        mh = MunicipalityHistory()
        mh.dates = self.dates
        mh.solarGenerators = self.solarGenerators
        mh.solarGeneratorsMapped = self.solarGeneratorsMapped
        
        if self.missingCommercialGenerators:
            mh.missingCommercialGenerators = []
            for ref in self.missingCommercialGenerators:
                if ref:
                    cgi = CommercialGeneratorInfo(mastrReference=ref)
                    mh.missingCommercialGenerators.append(cgi)
        return mh


if __name__ == "__main__":
    from glob import glob
    import pydantic
    import json
    from pydantic.json import pydantic_encoder

    for file_name in glob("docs/data/*.json"):
        print(file_name)
        try:
            m = pydantic.parse_file_as(path=file_name, type_=MunicipalityHistoryV1)
            mv2 = m.convert_to_v2()
            with open(file_name, "w") as f:
                f.write(
                    json.dumps(mv2, indent=4, default=pydantic_encoder)
                )
        except pydantic.error_wrappers.ValidationError:
            print("Parsing failed, skipping %s" % file_name)
