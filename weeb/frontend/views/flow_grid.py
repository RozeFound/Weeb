# flow_grid.py
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

from gi.repository import Gtk

from weeb.backend.settings import Settings

class FlowGridChild(Gtk.Box):

    __gtype_name__ = "FlowGridChild"

    settings = Settings()

    def __init__(self, **kwargs):

        orientation = self.settings.get("board/orientation", 0)
        tile_size = self.settings.get("board/tile/size", 180)

        super().__init__(**kwargs, spacing=10,
            margin_bottom=5, margin_top=5, margin_start=5, margin_end=5,
            halign=Gtk.Align.START, valign=Gtk.Align.START,
            orientation=orientation,
            width_request=tile_size if orientation == Gtk.Orientation.VERTICAL else 0,
            height_request=tile_size if orientation == Gtk.Orientation.HORIZONTAL else 0
        )

    def append(self, widget: Gtk.Widget) -> None:

        parent_width, parent_height = self.get_size_request()
        widget_width, widget_height = widget.get_size_request()

        if self.get_orientation() == Gtk.Orientation.VERTICAL:
            self.set_size_request(parent_width, parent_height + widget_height)
        elif self.get_orientation() == Gtk.Orientation.HORIZONTAL: 
            self.set_size_request(parent_width + widget_width, parent_height)

        super().append(widget)

class FlowGrid(Gtk.Box):

    __gtype_name__ = "FlowGrid"

    settings = Settings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_orientation(not self.settings.get("board/orientation", 0))

        self.children: list[FlowGridChild] = [FlowGridChild() for _ in range(4)]
        for child in self.children: super().append(child)

    def get_shortest_child(self) -> FlowGridChild:
        return min(self.children, key=lambda child: child.get_size_request()[not self.get_orientation()])

    def append(self, widget: Gtk.Widget) -> None:
        child = self.get_shortest_child()
        child.append(widget)