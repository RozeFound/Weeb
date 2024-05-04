# primitives.py
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

from abc import ABC
from dataclasses import dataclass
from typing import Callable, Optional

from weeb.backend.downloader import Downloader
from weeb.backend.settings import Settings
from weeb.backend.utils.expected import Expected


@dataclass(init=True)
class Variant:

    width: int
    height: int
    url: str

@dataclass(init=True)
class Asset:

    def __hash__(self) -> int:
        return hash(self.id) + hash(self.hash)

    id: int
    hash: str 

    variants: list[Variant]

    preview: Variant
    sample: Optional[Variant]
    original: Variant


class Booru(ABC):

    def __init__(self, name: str, base_url: str) -> None:

        self.__name = name
        self.__is_alive: bool = None

        self.base_url = base_url

        self.downloader = Downloader()
        self.settings = Settings()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def is_alive(self) -> bool:
        if self.__is_alive is None:
            self.test_availability()
        return self.__is_alive

    @is_alive.setter
    def is_alive(self, value: bool) -> None:
        self.__is_alive = value

    def test_availability(self) -> Expected:
        raise NotImplementedError("Derived classes must implement this method")

    def search_assets_async(self, tags: list, callback: Callable) -> Expected[set[Asset]]:
        raise NotImplementedError("Derived classes must implement this method")

    def search_tags_async(self, query: str, callback: Callable) -> Expected[set[str]]:
        raise NotImplementedError("Derived classes must implement this method")