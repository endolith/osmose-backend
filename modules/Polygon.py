#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frederic Rodrigo 2013-2018                                 ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from shapely.wkt import loads
from shapely.geometry import MultiPolygon
from modules import downloader
import pyproj
from shapely.ops import transform


class Polygon:

    def __init__(self, polygon_id, cache_delay=60):
        # polygon_id can be an integer, or a list of integers
        if isinstance(polygon_id, int):
            polygon_id = (polygon_id, )

        polygon_url = u"http://polygons.openstreetmap.fr/"
        for id in polygon_id:
            url = f"{polygon_url}index.py?id={str(id)}"
            downloader.urlread(url, cache_delay)
        url = f"{polygon_url}get_wkt.py?params=0&id=" + ",".join(map(str, polygon_id))
        self.wkt = wkt = downloader.urlread(url, cache_delay)
        if wkt.startswith("SRID="):
            wkt = wkt.split(";", 1)[1]
        self.polygon = loads(wkt)

    def as_simplified_wkt(self, out_src, metric_src) -> str:
        wgs84 = pyproj.CRS('EPSG:4326')
        metric_src = pyproj.CRS(f'EPSG:{metric_src}')
        out_src = pyproj.CRS(f'EPSG:{out_src}')
        project_metric = pyproj.Transformer.from_crs(wgs84, metric_src, always_xy=True).transform
        project_out = pyproj.Transformer.from_crs(metric_src, out_src, always_xy=True).transform

        out_poly = transform(project_metric, self.polygon)
        out_poly = out_poly.buffer(5000).simplify(5000)

        out_poly = transform(project_out, out_poly)
        return out_poly

    def bboxes(self):
        bbox = self.polygon.bounds
        if bbox[0] >= -179 or bbox[2] <= 179:
            return [bbox]
        negative = []
        positive = []
        for polygon in self.polygon.geoms:
            sub_bbox = polygon.bounds
            if sub_bbox[0] < 0:
                negative.append(polygon)
            else:
                positive.append(polygon)
        return [
            MultiPolygon(negative).bounds,
            MultiPolygon(positive).bounds,
        ]


###########################################################################
import unittest

class Test(unittest.TestCase):

    def test(self):
        # France
        p = Polygon(1403916)
        b = p.bboxes()
        self.assertNotEqual(b, None)
        self.assertEqual(len(b), 1)

        # Alaska
        p = Polygon(1116270)
        b = p.bboxes()
        self.assertNotEqual(b, None)
        self.assertEqual(len(b), 2)

        # Two texas counties
        p = Polygon((1812313,1812314))
        b = p.bboxes()
        self.assertNotEqual(b, None)
        self.assertEqual(len(b), 1)

        # Four texas counties
        p = Polygon((1812313,1812314,1809481,1827113))
        b = p.bboxes()
        self.assertNotEqual(b, None)
        self.assertEqual(len(b), 1)
