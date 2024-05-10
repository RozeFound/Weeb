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
from typing import Callable, Optional

from gi.repository import Adw, GObject, Gtk

from weeb.backend.constants import root
from weeb.backend.providers_manager import ProvidersManager
from weeb.backend.utils.expected import Expected


class Action(GObject.GEnum):
    NONE = 0
    REMOVE = 1
    ADD = 2


@Gtk.Template(resource_path=f"{root}/ui/tag.ui")
class Tag(Gtk.FlowBoxChild):
    __gtype_name__ = "Tag"

    remove_btn: Gtk.Button = Gtk.Template.Child()
    add_btn: Gtk.Button = Gtk.Template.Child()

    label: str = GObject.Property(type=str)

    def __init__(self, label: str, action: Action = Action.NONE) -> None:
        super().__init__()

        self.label = label
        if action: self.add_action(action)

        color_id = Random(self.label).randint(1, 35)
        self.style = f"custom_color_{color_id}"
        self.add_css_class(self.style)

    def get_action_btn(self, action: Action) -> Gtk.Button:

        match action:
            case Action.ADD: return self.add_btn
            case Action.REMOVE: return self.remove_btn

    def add_action(self, action: Action, callback: Optional[Callable] = None) -> None:

        btn = self.get_action_btn(action)
        if callback: btn.connect("clicked", callback)
        btn.set_visible(True)

    def remove_action(self, action: Optional[Action] = None) -> None:

        if not action:
            self.remove_action(Action.REMOVE)
            self.remove_action(Action.ADD)
            return

        btn = self.get_action_btn(action)
        btn.disconnect("clicked")
        btn.set_visible(False)


@Gtk.Template(resource_path=f"{root}/ui/tags.ui")
class Tags(Gtk.Box):
    __gtype_name__ = "Tags"

    meta_flow: Gtk.FlowBox = Gtk.Template.Child()
    selected_flow: Gtk.FlowBox = Gtk.Template.Child()
    dialog_flow: Gtk.FlowBox = Gtk.Template.Child()

    add_tag_dialog: Adw.Dialog = Gtk.Template.Child()
    tag_search: Adw.EntryRow = Gtk.Template.Child()

    selected_tags: list[Tag] = list()
    dialog_tags: list[Tag] = list()

    def __init__(self) -> None:
        super().__init__()

        self.app = Adw.Application.get_default()
        self.manager = ProvidersManager()

        self.fill_test_tags()
        self.fill_meta_tags()


    def fill_test_tags(self) -> None:

        test_tags = ("1girl", "1boy", "rating:sensitive")

        for tag in test_tags:
            tag = Tag(tag, Action.REMOVE)
            self.selected_flow.append(tag)
            self.selected_tags.append(tag)

    def fill_meta_tags(self) -> None:

        meta_types = ("type:image", "type:gif", "type:video")
        meta_ratings = ("rating:sensitive", "rating:general", "rating:questionable", "rating:explicit")
        
        for meta in (*meta_types, *meta_ratings):
            tag = Tag(meta, Action.ADD)
            if tag not in self.selected_tags:
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
                tag = Tag(tag, Action.ADD)
                self.dialog_flow.append(tag)
                self.dialog_tags.append(tag)

        def run_search() -> None:
            self.e_tags = self.manager.search_tags_async(self.tag_search.get_text(), helper)

        if hasattr(self, 'e_tags') and self.e_tags.is_running(): 
            self.e_tags.on_finish(run_search)
        else: run_search()
