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

import logging, math
from gi.repository import Gtk

from weeb.backend.constants import root
from weeb.backend.primitives import Asset, Variant
from weeb.backend.settings import Settings
from weeb.frontend.widgets.stream_image import StreamImage

@Gtk.Template(resource_path=f"{root}/ui/tile.ui")
class Tile(Gtk.Button):

    __gtype_name__ = "Tile"

    picture: Gtk.Picture = Gtk.Template.Child()

    settings = Settings()

    def __init__(self, asset: Asset, **kwargs):
        super().__init__(**kwargs)

        self.asset = asset
        self.variant = self.get_preferred_variant(asset)

        self.set_size_request(*self.get_preferred_size(self.variant))
        self.picture.set_paintable(StreamImage(self.variant, preload=False))

    def get_preferred_variant(self, asset: Asset) -> Variant:

        variant_index = 0

        image_orientation = int(asset.preview.width < asset.preview.height)
        board_orientation = self.settings.get("board/orientation", 0)

        min_preview = self.settings.get("board/tile/min_preview", 120)

        if image_orientation == board_orientation:

            for variant in asset.variants:
                axis = variant.width if image_orientation else variant.height
                if axis < min_preview and not variant.url.endswith((".mp4", ".gif")):
                   variant_index += 1
                else: break

        return asset.variants[variant_index]

    def get_preferred_size(self, variant: Variant) -> tuple[int, int]:

        width = height = tile_size = self.settings.get("board/tile/size", 180)
        board_orientation = self.settings.get("board/orientation", 0)

        if board_orientation == Gtk.Orientation.HORIZONTAL:
            width = math.floor((variant.width / variant.height) * tile_size)
        elif board_orientation == Gtk.Orientation.VERTICAL:
            height = math.floor((variant.height / variant.width) * tile_size)

        return width, height

    @Gtk.Template.Callback()
    def on_clicked(self, *args) -> None:

        logging.info(f"Tile {self.asset.id} clicked")
        logging.info(f"Asset hash: {self.asset.hash}")

        for variant in self.asset.variants:
            width, height, url = variant.width, variant.height, variant.url
            logging.info(f"Variant: {width}x{height} ({url})")

        width, height, url = self.variant.width, self.variant.height, self.variant.url
        logging.info(f"Chosen: {width}x{height} ({url})")

        logging.info(f"Tile size: {self.get_allocated_width()}x{self.get_allocated_height()}")
        logging.info(f"Tile requested size: {self.get_size_request()[0]}x{self.get_size_request()[1]}")