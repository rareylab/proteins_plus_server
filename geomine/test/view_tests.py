"""GeoMine view tests"""
from proteins_plus.test.utils import PPlusTestCase, call_api

from ..views import GeoMineView


class ViewTests(PPlusTestCase):
    """GeoMine view tests"""

    def test_filter_file(self):
        """Test GeoMine with dummy filter file"""
        data = {
            'filter_file': 'dummy.xml'
        }
        response = call_api(GeoMineView, 'post', data)
        self.assertEqual(response.status_code, 202)
