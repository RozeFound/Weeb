# stream_image.py
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

from gi.repository import GObject, Gdk, Gtk, Graphene, GLib
from weeb.backend.utils.threading import Expected

from weeb.backend.primitives import Variant
from weeb.backend.downloader import Downloader


class StreamImage(GObject.GObject, Gdk.Paintable):

    __gtype_name__ = "StreamImage"

    def __init__(self, variant: Variant, preload: bool = False) -> None:

        self.downloader = Downloader()

        self.width = variant.width
        self.height = variant.height
        self.url = variant.url

        self.texture: Gdk.Texture = None

        self.initialized = False

        if preload:
            self._lazy_init()

        super().__init__()

    def _lazy_init(self) -> None:

        if self.initialized:
            return

        def update_data(data: Expected[bytes]) -> None:   
            buffer = GLib.Bytes.new(data.value)
            self.texture = Gdk.Texture.new_from_bytes(buffer)
            self.invalidate_contents()

        self.downloader.download_async(self.url, update_data)
        self.initialized = True

    def do_get_intrinsic_width(self) -> int: return self.width
    def do_get_intrinsic_height(self) -> int: return self.height
    def do_get_intrinsic_aspect_ratio(self) -> float: return self.width / self.height

    def do_get_current_image(self) -> Gdk.Paintable: 
        self._lazy_init()
        return self.texture

    def do_snapshot(self, snapshot: Gtk.Snapshot, width: float, height: float) -> None:

        rect = Graphene.Rect()
        rect = rect.init(0, 0, width, height)

        if texture := self.get_current_image():
            snapshot.append_texture(texture, rect)
        else: snapshot.append_color(Gdk.RGBA(), rect)