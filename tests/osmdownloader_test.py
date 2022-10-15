from osmdownloader import OsmDownloader
from geojson.feature import FeatureCollection


def create_feature_collection(properties):
    features = {"properties": properties}
    fc = FeatureCollection(features)
    return fc


def test_create_generator_with_capacity():
    od = OsmDownloader()
    properties = {"generator:output:electricity": "500"}
    generator = od.create_generator(create_feature_collection(properties))
    assert 500 == generator.capacity


def test_create_generator_with_commercial():
    od = OsmDownloader()
    properties = {"ref": "SRsdfksjdlfjsdklf", "operator": "PV operator"}
    generator = od.create_generator(create_feature_collection(properties))
    assert generator.is_commercial


def test_create_generator_with_node_id():
    pass
    # od = OsmDownloader()
    # properties = {"osm_id": 8}
    # generator = od.create_generator(create_feature_collection(properties))
    # assert generator.osm_id == 8
