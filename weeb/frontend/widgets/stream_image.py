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

from gi.repository import Gdk, GdkPixbuf, GLib, GObject, Graphene, Gtk

from weeb.backend.downloader import Downloader
from weeb.backend.primitives import Variant


class StreamImage(GObject.GObject, Gdk.Paintable):

    __gtype_name__ = "StreamImage"

    def __init__(self, variant: Variant, early_init: bool = False, preload: bool = False) -> None:
        super().__init__()

        self.downloader = Downloader()

        self.loader = GdkPixbuf.PixbufLoader()
        self.loader.connect("area-updated", self.area_updated)
        self.loader.connect("area-prepared", self.area_prepared)

        self.width = variant.width
        self.height = variant.height
        self.url = variant.url

        self.can_read = False
        self.initialized = False
        self.loaded = False

        self.texture: Gdk.Texture = None

        if preload:
            buffer = GLib.Bytes.new(self.downloader.download(self.url))
            self.texture = Gdk.Texture.new_from_bytes(buffer)
            self.initialized = self.loaded = True

        if early_init: self._lazy_init()

    def area_prepared(self, *args) -> None:
        self.can_read = True

    def area_updated(self, *args) -> None: 
        if self.can_read: 
            pixbuf = self.loader.get_pixbuf()
            self.texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            self.invalidate_contents()

    def _lazy_init(self) -> None:

        if self.initialized:
            return

        def finalize() -> None: 
            self.loader.close()
            self.invalidate_contents()
            self.loaded = True

        def update_data(data: bytes) -> None:    
            buffer = GLib.Bytes.new(data)
            self.loader.write_bytes(buffer)

        e_bytes = self.downloader.download_async(self.url, update_data, stream=True)
        e_bytes.set_on_finish(finalize)

        self.initialized = True

    def do_get_intrinsic_width(self) -> int: return self.width
    def do_get_intrinsic_height(self) -> int: return self.height
    def do_get_intrinsic_aspect_ratio(self) -> float: return self.width / self.height
    def do_get_current_image(self) -> Gdk.Paintable: return self.texture
    def do_get_flags(self) -> Gdk.PaintableFlags: 
        flags = Gdk.PaintableFlags.SIZE
        if self.loaded: flags |= Gdk.PaintableFlags.CONTENTS
        return Gdk.PaintableFlags(flags)

    def do_snapshot(self, snapshot: Gtk.Snapshot, width: float, height: float) -> None:

        rect = Graphene.Rect()
        rect = rect.init(0, 0, width, height)

        if self.texture is not None:
            snapshot.append_texture(self.texture, rect)
        else: 
            self._lazy_init()
            snapshot.append_color(Gdk.RGBA(), rect)