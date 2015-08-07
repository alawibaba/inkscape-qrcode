#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# QRCode Generator Plugin
# plug-in version: 1.0
# by Ali Mohammad

# Based loosely on a plugin which calls a (defunct) web service to generate
# the qrcode. Since there are reasonable python libraries to generate qrcodes
# without going to the web, I changed this to just do it locally.

# Install: copy .inx and .py files to your Inkscape share\extensions directory
# Use: open Inkscape and select in menu: Extensions > Render > Barcode - QR Code...

# ***** BEGIN MIT LICENSE BLOCK *****
#
# Copyright (C) 2015 Ali Mohammad
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ***** END MIT LICENCE BLOCK *****

import inkex

import qrcode
import qrcode.image.svg

from StringIO import StringIO
from xml.etree.ElementTree import ElementTree

class QRCode(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
        # Get options
        self.OptionParser.add_option("--content", action="store", type="string", dest="content", default='')
        self.OptionParser.add_option("--size", action="store", type="int", dest="size", default=8)
        self.OptionParser.add_option("--padding", action="store", type="int", dest="padding", default=4)
        self.OptionParser.add_option("--version", action="store", type="string", dest="version", default='')
        self.OptionParser.add_option("--ec", action="store", type="string", dest="ec", default='M')
            
    def effect(self):
        # Check required parameters
        if len(self.options.content) == 0:
            inkex.errormsg(_('Please enter some content.'))
        else:
            # Create an element group in Inkscape
            transform = 'translate' + str(self.view_center)
            attribs = { inkex.addNS('label','inkscape'): 'QRCode', 'transform': transform }
            group = inkex.etree.SubElement(self.current_layer, 'g', attribs)
            
            # Render QR Code to the workspace
            self._render(group)

    def _render(self, parent):
        qrcode = self._generate()
        if not qrcode:
            return
        
        # Parse SVG and draw elements to the workspace
        output = StringIO()
        qrcode.save(output)
        output.seek(0)
        tree = ElementTree()
        tree.parse(output)
        root = tree.getroot()
    
        vbox = map(int, root.get("viewBox").split())
        vbox = vbox[0]-self.options.padding*self.options.size/10, \
               vbox[1]-self.options.padding*self.options.size/10, \
               vbox[2]+2*self.options.padding*self.options.size/10, \
               vbox[3]+2*self.options.padding*self.options.size/10
        vbox = map(str, vbox)
    
        rect = inkex.etree.SubElement(
                parent,
                inkex.addNS('rect', 'svg'),
                {"x": vbox[0],
                 "y": vbox[1],
                 "width": vbox[2],
                 "height": vbox[3],
                 "style": "fill:#fff;"})
        for m in root.getchildren():
            attribs = {}
            for k in m.keys():
                attribs[k] = str(m.get(k))
            inkex.etree.SubElement(parent, inkex.addNS('path', 'svg'), attribs)

    def _generate(self):
        attribs = {
            'border': 0,
            'box_size': int(self.options.size),
            'image_factory': qrcode.image.svg.SvgPathImage,
        }

        try:
            version = int(self.options.version)
            if version > 0:
                attribs['version'] = version
        except ValueError:
            pass

        ecc = {"L": qrcode.constants.ERROR_CORRECT_L,
               "M": qrcode.constants.ERROR_CORRECT_M,
               "Q": qrcode.constants.ERROR_CORRECT_Q,
               "H": qrcode.constants.ERROR_CORRECT_H}
        try:
            attribs['error_correction'] = ecc[self.options.ec]
        except KeyError:
            pass

        return qrcode.make(self.options.content, **attribs)

if __name__ == '__main__':
    e = QRCode()
    e.effect()
