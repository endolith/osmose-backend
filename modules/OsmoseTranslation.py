#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Jocelyn Jaubert 2013                                       ##
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

import os
import polib

class OsmoseTranslation:

    def __init__(self):
        self.languages = []
        self.trans = {}
        josm_po_path = "po/josm/"
        transport_mapcss_po_path = "po/transport_mapcss/"
        for fn in os.listdir("po/"):
            if os.path.isfile(os.path.join(josm_po_path, fn)):
                self.add_po(fn, josm_po_path)
            if os.path.isfile(os.path.join(transport_mapcss_po_path, fn)):
                self.add_po(fn, transport_mapcss_po_path)
            if fn.endswith(".po"):
                self.add_po(fn, "po/")

    def add_po(self, fn, base):
        l = fn[:-3]
        po = polib.pofile(base + l + ".po")
        if l not in self.trans:
            self.languages.append(l)
            self.trans[l] = {}
        for entry in po:
            if entry.msgstr != "":
                self.trans[l][entry.msgid] = entry.msgstr

    def translate(self, string, *args, **kwargs):
        out = {}

        if not args and not kwargs:
            out["en"] = string

            for l in self.languages:
                if (
                    string in self.trans[l]
                    and self.trans[l][string] != ""
                    and not args
                ):
                    out[l] = self.trans[l][string]

        else:
            args_basic = []
            args_translated = []
            for arg in args:
                if isinstance(arg, dict):
                    args_basic.append('{' + str(len(args_translated)) + '}')
                    args_translated.append(arg)
                elif isinstance(arg, str):
                    args_basic.append(arg.replace('{', '{{').replace('}', '}}'))
                else:
                    args_basic.append(arg)

            out["en"] = string.format(*args_basic, **kwargs)
            if args_translated:
                out["en"] = out["en"].format(*map(lambda a: a['en'], args_translated))

            for l in self.languages:
                if string in self.trans[l] and self.trans[l][string] != "":
                    out[l] = self.trans[l][string].format(*args_basic, **kwargs)
                    if args_translated:
                        out[l] = out[l].format(*map(lambda a: l in a and a[l] or a['en'], args_translated))

        return out

translate = OsmoseTranslation()

T_ = translate.translate

if __name__ == "__main__":
    translate = OsmoseTranslation()
    print("languages: ")
    for l in translate.languages:
        print(l, len(translate.trans[l]))
