# preferences.py
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

import logging
from gi.repository import Gtk, Adw

from weeb.backend.constants import root
from weeb.backend.settings import Settings

@Gtk.Template(resource_path=f"{root}/ui/preferences.ui")
class Preferences(Adw.PreferencesDialog):

    __gtype_name__ = "Preferences"

    proxy_type_row: Adw.ComboRow = Gtk.Template.Child()
    proxy_host_row: Adw.EntryRow = Gtk.Template.Child()
    proxy_port_btn: Gtk.SpinButton = Gtk.Template.Child() 
    proxy_general_apply_btn: Gtk.Button = Gtk.Template.Child()

    proxy_username_row: Adw.EntryRow = Gtk.Template.Child()
    proxy_password_row: Adw.EntryRow = Gtk.Template.Child()
    proxy_credentials_apply_btn: Gtk.Button = Gtk.Template.Child()

    settings = Settings()

    def __init__(self, **kwargs):
        super().__init__()

        self.app = kwargs.get("application")

        self.proxy_type_row.set_selected(self.settings.get("proxy/type", 0))
        self.proxy_host_row.set_text(self.settings.get("proxy/host", "127.0.0.1"))
        self.proxy_port_btn.set_value(self.settings.get("proxy/port", 8080))

        if credentials := self.settings.get("proxy/credentials"):
            username, password = credentials.values()
            self.proxy_username_row.set_text(username)
            self.proxy_password_row.set_text(password)

        self.proxy_general_apply_btn.set_sensitive(False)
        self.proxy_credentials_apply_btn.set_sensitive(False)

    @Gtk.Template.Callback()
    def on_proxy_type_selected(self, *args) -> None:

        enable = self.proxy_type_row.get_selected() != 0

        self.proxy_host_row.set_sensitive(enable)
        self.proxy_port_btn.set_sensitive(enable)
        self.proxy_username_row.set_sensitive(enable)
        self.proxy_password_row.set_sensitive(enable)

        self.on_proxy_general_changed()

    @Gtk.Template.Callback()
    def on_proxy_general_changed(self, *args) -> None:
        self.proxy_general_apply_btn.set_sensitive(True)

    @Gtk.Template.Callback()
    def on_proxy_credentials_changed(self, *args) -> None:
        self.proxy_credentials_apply_btn.set_sensitive(True)

    @Gtk.Template.Callback()
    def on_proxy_general_apply(self, *args) -> None:

        self.settings.set("proxy/type", self.proxy_type_row.get_selected())
        self.settings.set("proxy/host", self.proxy_host_row.get_text())
        self.settings.set("proxy/port", self.proxy_port_btn.get_value_as_int())

        self.proxy_general_apply_btn.set_sensitive(False)

        self.update_proxy_uri()

    @Gtk.Template.Callback()
    def on_proxy_credentials_apply(self, *args) -> None:

        self.settings.set("proxy/credentials/username", self.proxy_username_row.get_text())
        self.settings.set("proxy/credentials/password", self.proxy_password_row.get_text())

        self.proxy_credentials_apply_btn.set_sensitive(False)

        self.update_proxy_uri()

    def update_proxy_uri(self) -> None:

        logging.info("Updating proxy URI...")

        match self.settings.get("proxy/type"):
            case 0: self.settings.set("proxy/uri", None); return
            case 1: schema = "http://"
            case 2: schema = "https://"
            case 3: schema = "socks5://"

        host = self.settings.get("proxy/host")
        port = self.settings.get("proxy/port")

        if not host or not port: return

        userdata = ""

        if credentials := self.settings.get("proxy/credentials"):
            username, password = credentials.values()
            if username and password: userdata = f"{username}:{password}@" 

        self.settings.set("proxy/uri", f"{schema}{userdata}{host}:{port}")