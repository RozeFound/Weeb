# board.py
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

from gi.repository import Gtk, Adw, GObject

from weeb.backend.constants import root
from weeb.backend.utils.expected import Expected
from weeb.backend.primitives import Asset

from weeb.frontend.views.tile import Tile
from weeb.backend.providers_manager import ProvidersManager

@Gtk.Template(resource_path=f"{root}/ui/board.ui")
class Board(Adw.Bin):

    __gtype_name__ = "Board"

    placeholder: Adw.StatusPage = Gtk.Template.Child()
    scroll: Gtk.ScrolledWindow = Gtk.Template.Child()
    flow: Gtk.FlowBox = Gtk.Template.Child()

    items_per_line = GObject.property(type=int, default=0)

    def __init__(self, **kwargs):

        self.assets: set[Asset] = set()
        self.e_search: Expected[set[Asset]] = None

        super().__init__(**kwargs)

        self.manager = ProvidersManager()

    def search_by_tags(self, tags: list[str]) -> None:

        def run_search() -> None:
            self.e_search = self.manager.search_assets_by_tags_async(tags, self.populate_board)

        if self.e_search is not None and self.e_search.is_running():
            self.e_search.on_finish(run_search)
        else: run_search()

    def populate_board(self, e_assets: Expected[set[Asset]]) -> None:

        assets = e_assets.value

        for asset in assets:
            tile = Tile(asset)
            self.flow.append(tile)

        self.items_per_line = len(self.assets)

        self.placeholder.set_visible(len(assets) == 0)
        self.scroll.set_visible(len(assets) != 0)


