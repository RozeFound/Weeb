# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw

from weeb.frontend.views.window import WeebWindow
from weeb.backend.constants import app_id, version, root

class WeebApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id=app_id,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self.set_resource_base_path(root)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win: self.win = WeebWindow(application=self)
        self.win.present()

        self.create_action('quit', self.win.on_close_request, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action, ["<primary>comma"])

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='weeb',
                                application_icon=app_id,
                                developer_name='RozeFound',
                                version=version,
                                developers=['RozeFound'],
                                copyright='© 2024 RozeFound')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):

        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

        if shortcuts: self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = WeebApplication()
    return app.run(sys.argv)
