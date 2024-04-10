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

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio

import logging

from weeb.backend.constants import app_id, root

@Gtk.Template(resource_path=f'{root}/ui/window.ui')
class WeebWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'WeebWindow'

    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()

    label: Gtk.Label = Gtk.Template.Child()

    app = Gtk.Application.get_default()
    settings = Gio.Settings.new(app_id)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs,
            default_width=self.settings.get_int("width"),
            default_height=self.settings.get_int("height"))

        self.connect("close_request", self.on_close_request)
        self.connect("unrealize", self.on_unrealize)

    def on_close_request(self, *args):
        """Callback for the win.close_request event."""
        
        self.close()

    def on_unrealize(self, *args):
        """Callback for the win.unrealize event."""

        width, height = self.get_default_size()
        self.settings.set_int('width', width)
        self.settings.set_int('height', height)

    def on_toggle_search_action(self, *args):
        """Callback for the win.toggle_search action."""

        search_mode = not self.search_bar.get_search_mode()
        self.search_bar.set_search_mode(search_mode)

        if search_mode:
            self.set_focus(self.search_entry)

        self.search_entry.set_text("")