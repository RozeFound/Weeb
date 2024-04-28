# settings.py
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

from collections import defaultdict
import json, logging, pathlib, enum
from typing import Any, Callable, Optional
from gi.repository import Gio, Gtk

from weeb.backend.constants import app_id
from weeb.backend.utils.paths import Paths
from weeb.backend.utils.singleton import Singleton

class Priority(enum.Enum):
    LOW = 0
    HIGH = 1

class _PartialGSettings:

    def __init__(self):
        self._settings = Gio.Settings.new(app_id)

    def bind(self, key: str, obj: object, property: str, flags: Gio.SettingsBindFlags = Gio.SettingsBindFlags.DEFAULT) -> None:
        self._settings.bind(key, obj, property, flags)

    def get_int(self, key: str) -> int: return self._settings.get_int(key)
    def get_string(self, key: str) -> str: return self._settings.get_string(key)
    def get_boolean(self, key: str) -> bool: return self._settings.get_boolean(key)

    def set_int(self, key: str, value: int) -> bool: return self._settings.set_int(key, value)
    def set_string(self, key: str, value: str) -> bool: return self._settings.set_string(key, value)
    def set_boolean(self, key: str, value: bool) -> bool: return self._settings.set_boolean(key, value)

class Settings(_PartialGSettings, metaclass=Singleton):

    def __init__(self) -> None:
        super().__init__()
        
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.config_path = Paths.get("config/settings.json", parents=True)
        self.config: dict = self.read(self.config_path)

        self._is_closed = False

    def close(self) -> None:
        if not self._is_closed:
            self.write(self.config_path)
            self._is_closed = True

    def read(self, path: pathlib.Path) -> dict:

        config = dict()
        
        try:
            with open(path, "r") as file:
                config = json.load(file)

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse config file: {e}")

        except OSError as e:
            logging.error(f"Failed to find config file: {e}")

        return config

    def write(self, path: pathlib.Path) -> None:
        
        try:
            with open(path, "w") as file:
                json.dump(self.config, file, indent=4)

        except OSError as e:
            logging.error(f"Failed to write config file: {e}")

    def on_changed(self, changed_key: str, changed_value: Any) -> None:
        """
        Allows for partial subs like this:

        >>> settings.connect("proxy", callback)

        The callback will trigger if any of proxy subfields are changed
        """

        self.write(self.config_path)

        for key, callbacks in self.subscribers.items():
            if key not in changed_key: continue

            for callback in callbacks:
                callback(changed_value)


    def _get_path(self, path: str, default: Any) -> Optional[Any]:

        parts = path.split('/')
        doc = self.config

        for part in parts:
            if part not in doc:
                return default
            doc = doc[part]

        return doc

    def _set_path(self, path: str, value: Any) -> None:

        parts = path.split('/')
        doc = self.config

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                doc[part] = value
            elif part not in doc:
                doc[part] = {}
            doc = doc[part]
                
    def get(self, key: str, default: Any = None) -> Optional[Any]:

        if '/' in key: 
            return self._get_path(key, default)
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> Any:

        old_value = self.get(key)

        if old_value != value:
        
            if '/' in key: 
                self._set_path(key, value) 
            else: self.config[key] = value

            self.on_changed(key, value)

        return old_value

    def connect(self, key: str, callback: Callable, priority: Priority = Priority.LOW) -> None:
        if priority == Priority.HIGH:
            self.subscribers[key].insert(0, callback)
        else: self.subscribers[key].append(callback)

