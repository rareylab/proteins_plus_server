"""Configuration for GeoMine tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    filter_file = testdir / 'dummyGeoMineFilter.xml'
    geomine_result_file = testdir / 'geomine_result.json'
