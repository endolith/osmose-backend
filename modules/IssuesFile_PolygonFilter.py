#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frederic Rodrigo 2013-2016                                 ##
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

from .PointInPolygon import PointInPolygon


class IssuesFilter:
    def apply(self, classs, subclass, geom):
        return True


class PolygonFilter(IssuesFilter):

    def __init__(self, polygon_id, cache_delay=60):
        self.pip = PointInPolygon(polygon_id, cache_delay)

    def apply(self, classs, subclass, geom):
        if "position" not in geom:
            return False
        inside = False
        for position in geom["position"]:
            lat = float(position["lat"])
            inside |= self.pip.point_inside_polygon(float(position["lon"]), lat)
        return inside
