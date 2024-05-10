# window.py
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

from gi.repository import Adw, Gtk

from weeb.backend.constants import debug, root
from weeb.backend.settings import Settings
from weeb.frontend.views.board import Board
from weeb.frontend.views.tags import Tags


@Gtk.Template(resource_path=f'{root}/ui/window.ui')
class WeebWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'WeebWindow'

    split_view: Adw.OverlaySplitView = Gtk.Template.Child()

    board: Board = Gtk.Template.Child()
    tags: Tags = Gtk.Template.Child()
    
    settings = Settings()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs,
            default_width=self.settings.get_int("window-width"),
            default_height=self.settings.get_int("window-height"),
            maximized=self.settings.get_boolean("window-maximized"))

        self.tags.connect("tags-changed", self.on_tags_changed)
        self.connect("close_request", self.on_close_request)
        self.connect("unrealize", self.on_unrealize)

        if debug: self.add_css_class("devel")

    def on_close_request(self, *args) -> None:
        """Callback for the win.close_request event."""
        self.settings.close()

    def on_unrealize(self, *args) -> None:
        """Callback for the win.unrealize event."""

        width, height = self.get_default_size()
        maximized = self.is_maximized()
        
        self.settings.set_int('window-width', width)
        self.settings.set_int('window-height', height)
        self.settings.set_boolean('window-maximized', maximized)

    def on_tags_changed(self, widget: Tags, tags: list[str]) -> None:
        self.board.search_by_tags(tags)

    def on_toggle_sidebar_action(self, *args) -> None:
        self.split_view.set_show_sidebar(not self.split_view.get_show_sidebar())