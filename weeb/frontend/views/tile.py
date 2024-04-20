# tile.py
#
# Copyright 2024 RozeFound
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk, Gdk, GObject

from weeb.backend.constants import root
from weeb.backend.primitives import Asset
from weeb.frontend.views.stream_image import StreamImage

@Gtk.Template(resource_path=f"{root}/ui/tile.ui")
class Tile(Gtk.Box):

    __gtype_name__ = "Tile"

    paintable = GObject.Property(type=Gdk.Paintable)

    def __init__(self, asset: Asset, **kwargs):

        self.variant = asset.preview

        super().__init__(**kwargs,
            width_request=self.variant.width,
            height_request=self.variant.height)

        self.paintable = StreamImage(self.variant)