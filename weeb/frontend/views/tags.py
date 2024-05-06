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

from random import Random

from gi.repository import Adw, GObject, Gtk

from weeb.backend.constants import root
from weeb.backend.providers_manager import ProvidersManager
from weeb.backend.utils.expected import Expected


class HoverAction(GObject.GEnum):
    REMOVE = 0
    ADD = 1


@Gtk.Template(resource_path=f"{root}/ui/tag.ui")
class Tag(Gtk.FlowBoxChild):
    __gtype_name__ = "Tag"

    remove_btn: Gtk.Button = Gtk.Template.Child()
    add_btn: Gtk.Button = Gtk.Template.Child()

    label: str = GObject.Property(type=str)
    hover_action: HoverAction

    def __init__(self, label: str = ..., hover_action: HoverAction = ...) -> None:
        super().__init__()

        self.label = label
        self.hover_action = hover_action 

        color_id = Random(self.label).randint(1, 35)
        self.style = f"custom_color_{color_id}"
        self.add_css_class(self.style)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("enter", self.on_motion_enter)
        motion_controller.connect("leave", self.on_motion_leave)
        self.add_controller(motion_controller)

    def on_motion_enter(self, *args) -> None:

        if self.hover_action == HoverAction.REMOVE:
            self.remove_btn.set_visible(True)
        elif self.hover_action == HoverAction.ADD:
            self.add_btn.set_visible(True)

    def on_motion_leave(self, *args) -> None:

        if self.hover_action == HoverAction.REMOVE:
            self.remove_btn.set_visible(False)
        elif self.hover_action == HoverAction.ADD:
            self.add_btn.set_visible(False)


@Gtk.Template(resource_path=f"{root}/ui/tags.ui")
class Tags(Gtk.Box):
    __gtype_name__ = "Tags"

    meta_flow: Gtk.FlowBox = Gtk.Template.Child()
    selected_flow: Gtk.FlowBox = Gtk.Template.Child()
    dialog_flow: Gtk.FlowBox = Gtk.Template.Child()

    add_tag_dialog: Adw.Dialog = Gtk.Template.Child()
    tag_search: Adw.EntryRow = Gtk.Template.Child()

    dialog_tags = list()

    def __init__(self) -> None:
        super().__init__()

        self.app = Adw.Application.get_default()
        self.manager = ProvidersManager()

        self.fill_meta_tags()
        self.fill_test_tags()

    def fill_test_tags(self) -> None:

        test_tags = ("1girl", "1boy", "rating:sensitive")

        for tag in test_tags:
            tag = Tag(tag, HoverAction.REMOVE)
            self.selected_flow.append(tag)

    def fill_meta_tags(self) -> None:

        meta_types = ("type:image", "type:gif", "type:video")
        meta_ratings = ("rating:sensitive", "rating:general", "rating:questionable", "rating:explicit")
        
        for meta in (*meta_types, *meta_ratings):
            tag = Tag(meta, HoverAction.ADD)
            self.meta_flow.append(tag)

    #@Gtk.Template.Callback()
    def on_add_tag_clicked(self, *args) -> None:
        self.add_tag_dialog.present(self.app.window)

    @Gtk.Template.Callback()
    def on_tag_search_changed(self, *args) -> None:

        def helper(_e_tags: Expected[set[str]]) -> None:

            for tag in self.dialog_tags:
                self.dialog_flow.remove(tag)

            self.dialog_tags.clear()

            for tag in _e_tags.value:
                tag = Tag(tag, HoverAction.ADD)
                self.dialog_flow.append(tag)
                self.dialog_tags.append(tag)

        def run_search() -> None:
            self.e_tags = self.manager.search_tags_async(self.tag_search.get_text(), helper)

        if hasattr(self, 'e_tags') and self.e_tags.is_running(): 
            self.e_tags.on_finish(run_search)
        else: run_search()
