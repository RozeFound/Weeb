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

import logging
from random import Random
from typing import Callable, Optional

from gi.repository import Adw, GLib, GObject, Gtk

from weeb.backend.constants import root
from weeb.backend.providers_manager import ProvidersManager
from weeb.backend.settings import Settings
from weeb.backend.utils.expected import Expected


class Action(GObject.GEnum):
    NONE = 0
    REMOVE = 1
    ADD = 2


@Gtk.Template(resource_path=f"{root}/ui/tag.ui")
class Tag(Gtk.FlowBoxChild):
    __gtype_name__ = "Tag"

    action_btn: Gtk.Button = Gtk.Template.Child()
    action_id: int | None = None

    label: str = GObject.Property(type=str)

    def __init__(self, label: str, action: Action = Action.NONE) -> None:
        super().__init__()

        self.label = label
        if action: self.set_action(action)

        color_id = Random(self.label).randint(1, 35)
        self.style = f"custom_color_{color_id}"
        self.add_css_class(self.style)

    def __eq__(self, other: object) -> bool:
        return self.label == other.label

    def set_action(self, action: Action, callback: Optional[Callable] = None) -> None:

        self.action_btn.remove_css_class("destructive-action")
        self.action_btn.remove_css_class("suggested-action")
        
        match action:
            case Action.REMOVE:
                self.action_btn.set_icon_name("cross-large-circle-filled-symbolic")
                self.action_btn.add_css_class("destructive-action")
            case Action.ADD:
                self.action_btn.set_icon_name("plus-large-circle-symbolic")
                self.action_btn.add_css_class("suggested-action")

        self.action_btn.set_visible(action != Action.NONE)

    def remove_callback(self) -> None:

        if self.action_id is not None:
            self.action_btn.disconnect(self.action_id)

    def set_callback(self, callback: Callable, *args, **kwargs) -> None:

        self.remove_callback()

        if kwargs: args += tuple([value for _, value in kwargs])
        self.action_id = self.action_btn.connect("clicked", callback, *args)

@Gtk.Template(resource_path=f"{root}/ui/tags.ui")
class Tags(Gtk.Box):
    __gtype_name__ = "Tags"

    meta_flow: Gtk.FlowBox = Gtk.Template.Child()
    selected_flow: Gtk.FlowBox = Gtk.Template.Child()
    search_flow: Gtk.FlowBox = Gtk.Template.Child()

    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    search_box: Gtk.Box = Gtk.Template.Child()

    selected_tags: list[Tag] = list()
    search_tags: list[Tag] = list()
    meta_tags: list[Tag] = list()

    settings = Settings()

    def __init__(self) -> None:
        super().__init__()

        self.app = Adw.Application.get_default()
        self.manager = ProvidersManager()

        self.fill_selected_tags()
        self.fill_meta_tags()

        GLib.timeout_add_seconds(2, self.emit, "tags-changed", self.get_tags())

    def fill_selected_tags(self) -> None:

        if tags := self.settings.get("tags"):
            for tag in tags: 
                tag = Tag(tag, Action.REMOVE)
                tag.set_callback(self.remove_tag, tag)
                self.selected_flow.append(tag)
                self.selected_tags.append(tag)

    def fill_meta_tags(self) -> None:

        meta_types = ("type:image", "type:gif", "type:video")
        meta_ratings = ("rating:sensitive", "rating:general", "rating:questionable", "rating:explicit")
        
        for meta in (*meta_types, *meta_ratings):
            tag = Tag(meta, Action.ADD)
            if tag not in (*self.meta_tags, *self.selected_tags):
                tag.set_callback(self.add_tag, tag)
                self.meta_flow.append(tag)
                self.meta_tags.append(tag)

    def get_tags(self) -> list[str]:
        return [tag.label for tag in self.selected_tags]

    @GObject.Signal(name="tags-changed", arg_types=(object,), flags=GObject.SignalFlags.RUN_LAST)
    def tags_changed(self, tags: list[str]) -> None:
        logging.info(f"Tags selection changed to: {', '.join(tags)}")
        self.settings.set("tags", tags)

    def update_visibility(self) -> None:

        self.selected_flow.set_visible(bool(self.selected_tags))
        self.search_flow.set_visible(bool(self.search_tags))
        self.meta_flow.set_visible(bool(self.meta_tags))

    def add_tag(self, widget: Gtk.Widget, tag: Tag) -> None:

        if tag in self.meta_tags:
            self.meta_flow.remove(tag)
            self.meta_tags.remove(tag)

        if tag in self.search_tags:
            self.search_flow.remove(tag)
            self.search_tags.remove(tag)

        if tag not in self.selected_tags:
            self.selected_flow.append(tag)
            self.selected_tags.append(tag)
            
        tag.set_action(Action.REMOVE)
        tag.set_callback(self.remove_tag, tag)
        self.update_visibility()
        self.emit("tags-changed", self.get_tags())

    def remove_tag(self, widget: Gtk.Widget, tag: Tag) -> None:

        if tag in self.selected_tags:
            self.selected_flow.remove(tag)
            self.selected_tags.remove(tag)

        self.fill_meta_tags()
        self.update_visibility()
        self.emit("tags-changed", self.get_tags())

    @Gtk.Template.Callback()
    def on_tag_search_changed(self, *args) -> None:

        def helper(_e_tags: Expected[set[str]]) -> None:

            for tag in self.search_tags:
                self.search_flow.remove(tag)

            self.search_tags.clear()

            for tag in _e_tags.value:

                tag = Tag(tag, Action.ADD)

                if tag not in self.selected_tags:
                    tag.set_callback(self.add_tag, tag)
                    self.search_flow.append(tag)
                    self.search_tags.append(tag)

            self.search_box.set_visible(True)
            self.update_visibility()

        def run_search() -> None:
            self.e_tags = self.manager.search_tags_async(self.search_entry.get_text(), helper)

        if self.search_entry.get_text() == "":
            self.search_box.set_visible(False)
            return

        if hasattr(self, 'e_tags') and self.e_tags.is_running(): 
            self.e_tags.on_finish(run_search)
        else: run_search()
