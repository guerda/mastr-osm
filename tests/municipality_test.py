from municipality import MunicipalityHistory
from datetime import datetime
import pydantic


def test_simple():
    m = MunicipalityHistory()
    m.dates = [datetime.now(), datetime.now()]
    m.solarGenerators = [0, 1, 2]
    m.solarGeneratorsMapped = [0, 0, 1]
    assert 2 == len(m.dates)
    assert [0, 1, 2] == m.solarGenerators
    assert [0, 0, 1] == m.solarGeneratorsMapped


def test_represent_as_json():
    m = MunicipalityHistory()
    m.dates = [datetime(2022, 1, 31, 14, 1, 3, 3)]
    m.solarGenerators = [0, 1, 2]
    m.solarGeneratorsMapped = [0, 0, 1]
    m_json = m.json()
    assert (
        """{"dates": ["2022-01-31T14:01:03.000003"], "solarGenerators": [0, 1, 2],"""
        """ "solarGeneratorsMapped": [0, 0, 1],"""
        """ "missingCommercialGenerators": []}""" == m_json
    )


def test_load_from_json():
    m = pydantic.parse_file_as(path="tests/history.json", type_=MunicipalityHistory)
    assert len(m.dates) == 3
    assert len(m.solarGenerators) == 3
    assert len(m.solarGeneratorsMapped) == 3
    assert m.solarGenerators == [20, 34, 40]
    assert m.solarGeneratorsMapped == [1, 2, 3]
