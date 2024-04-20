# paths.py
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

import os, pathlib, functools

class Paths:

    @staticmethod
    def get_from_env(env_var: str, fallback: str) -> pathlib.Path:
        fallback = os.path.join(pathlib.Path.home(), fallback)
        return pathlib.Path(os.environ.get(env_var, fallback))

    @staticmethod
    @functools.cache
    def get_location(loc: str) -> pathlib.Path:
        if loc == "cache": return Paths.get_from_env("XDG_CACHE_HOME", ".cache")
        if loc == "config": return Paths.get_from_env("XDG_CONFIG_HOME", ".config")
        return Paths.get_from_env("XDG_DATA_HOME", ".local/share")
    
    @staticmethod
    def get(str_path: str, parents = False) -> pathlib.Path:

        parts = str_path.split("/")
        if not parts: return

        path = Paths.get_location(parts[0]) / "weeb"
        if (parts[0] in ("cache", "config")): parts.pop(0)
        for part in parts: path /= part

        if parents:
            path.parent.mkdir(parents=True, exist_ok=True)

        return path