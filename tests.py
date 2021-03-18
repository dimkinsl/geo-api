import unittest

from geo.get_distance import in_polygon_coordinates, haversine
from geo.base_coordinates import MKAD


class FunctionsTest(unittest.TestCase):

    def test_in_polygon(self):
        in_mkad_x = 55.700182
        in_mkad_y = 37.580158
        result = in_polygon_coordinates(in_mkad_x, in_mkad_y, MKAD)
        self.assertEqual(result, True)

    def test_not_in_polygon(self):
        in_mkad_x = 55.527667
        in_mkad_y = 37.445401
        result = in_polygon_coordinates(in_mkad_x, in_mkad_y, MKAD)
        self.assertEqual(result, False)

    def test_haversine(self):
        lat1 = 51.837897
        lon1 = 55.147944
        result = haversine(lat1, lon1, MKAD)
        self.assertEqual(result, 1211.26)


if __name__ == '__main__':
    unittest.main(verbosity=2)
