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

import logging, subprocess

from gi.repository import Adw, Gtk

from weeb.backend.constants import root
from weeb.backend.settings import Settings


@Gtk.Template(resource_path=f"{root}/ui/preferences.ui")
class Preferences(Adw.PreferencesDialog):

    __gtype_name__ = "Preferences"

    open_config_file_btn: Gtk.Button = Gtk.Template.Child()
    open_config_folder_btn: Gtk.Button = Gtk.Template.Child()
    delete_config_file_btn: Gtk.Button = Gtk.Template.Child()

    board_orientation_row: Adw.ComboRow = Gtk.Template.Child()
    board_tile_size_row: Adw.SpinRow = Gtk.Template.Child()
    board_tile_min_preview_row: Adw.SpinRow = Gtk.Template.Child()
    general_board_apply_btn: Gtk.Button = Gtk.Template.Child()

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

        self.app: Adw.Application = kwargs.get("application")

        self.open_config_file_btn.connect("clicked", 
            lambda *args: self.settings.open_file(self.app.window))

        self.open_config_folder_btn.connect("clicked",
            lambda *args: self.settings.open_folder(self.app.window))

        self.set_values_from_config()

        self.general_board_apply_btn.set_sensitive(False)
        self.proxy_general_apply_btn.set_sensitive(False)
        self.proxy_credentials_apply_btn.set_sensitive(False)

    def set_values_from_config(self) -> None:

        self.board_orientation_row.set_selected(self.settings.get("board/orientation", 0))

        self.board_tile_size_row.set_value(self.settings.get("board/tile/size", 180))
        self.board_tile_min_preview_row.set_value(self.settings.get("board/tile/min_preview", 120))

        self.proxy_type_row.set_selected(self.settings.get("proxy/type", 0))
        self.proxy_host_row.set_text(self.settings.get("proxy/host", "127.0.0.1"))
        self.proxy_port_btn.set_value(self.settings.get("proxy/port", 8080))

        if credentials := self.settings.get("proxy/credentials"):
            username, password = credentials.values()
            self.proxy_username_row.set_text(username)
            self.proxy_password_row.set_text(password)

#region GENERAL

    @Gtk.Template.Callback()
    def on_delete_config_file_clicked(self, *args) -> None:

        def on_response_selected(dialog: Adw.Dialog, task) -> None:
            response = dialog.choose_finish(task)
            if response == "delete": 
                self.settings.delete_file()
        
        dialog = Adw.AlertDialog(
            heading="Are you sure?",
            body="You are going to delete the file containing all your data.\nIt will reset all the changes you made.",
            close_response="cancel")
            
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")

        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        dialog.choose(self, None, on_response_selected)

    @Gtk.Template.Callback()
    def on_general_board_changed(self, *args) -> None:
        self.general_board_apply_btn.set_sensitive(True)
        
    @Gtk.Template.Callback()
    def on_general_board_apply(self, *args) -> None:

        self.settings.set("board/orientation", self.board_orientation_row.get_selected())
        self.settings.set("board/tile/size", self.board_tile_size_row.get_value())
        self.settings.set("board/tile/min_preview", self.board_tile_min_preview_row.get_value())

        self.general_board_apply_btn.set_sensitive(False)

        def do_restart(*args) -> None:
            subprocess.Popen("sleep 1 && weeb & disown", shell=True)
            self.app.on_quit_action()

        toast = Adw.Toast(
            title="Some changes will take effect only restart",
            button_label="Relaunch Weeb")

        toast.connect("button-clicked", do_restart)

        self.add_toast(toast)

#endregion

#region PROXY

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

#endregion