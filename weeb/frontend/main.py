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

import logging

from gi.repository import Gio, Adw

from weeb.frontend.views.window import WeebWindow
from weeb.frontend.views.preferences import Preferences
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
        self.window = self.props.active_window
        if not self.window:
            self.window = WeebWindow(application=self)
        self.window.present()

        self.create_action('quit', ['<primary>q'])
        self.create_action('about')
        self.create_action('preferences', ["<primary>comma"])
        self.create_action('toggle_sidebar', ["<primary>s"], self.window)

    def on_quit_action(self, *args):
        """Callback for the app.quit action."""
        if hasattr(self, 'preferences'): self.preferences.close()
        if hasattr(self, 'window'): self.window.close()
        self.quit()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='Weeb',
                                application_icon=app_id,
                                developer_name='RozeFound',
                                version=version,
                                developers=['RozeFound'],
                                copyright='© 2024 RozeFound')
        about.present(self.window)

    def on_preferences_action(self, *args):
        """Callback for the app.preferences action."""
        self.preferences = Preferences(application=self)
        self.preferences.present(self.window)

    def create_action(self, name: str, shortcuts: list[str] = None, scope: object = None) -> None:

        scope = self if scope is None else scope

        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", getattr(scope, f"on_{name}_action"))
        scope.add_action(action)

        if shortcuts: 
            accel = f"app.{name}" if scope == self else f"win.{name}"
            self.set_accels_for_action(accel, shortcuts)

def setup_logging() -> None:
    format = "[%(asctime)s] [weeb] [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S.%03d"
    logging.basicConfig(level=logging.INFO, format=format, datefmt=datefmt)

def main(version: str):
    """The application's entry point."""
    setup_logging()
    app = WeebApplication()
    logging.info(f"Starting weeb v{version}")
    return app.run(sys.argv)
