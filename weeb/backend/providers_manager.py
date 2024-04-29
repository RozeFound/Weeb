# providers_manager.py
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

from typing import Any, Callable

from weeb.backend.primitives import Asset, Booru
from weeb.backend.providers.danbooru import DanBooru
from weeb.backend.settings import Settings
from weeb.backend.utils.expected import Expected
from weeb.backend.utils.singleton import Singleton


class ProvidersManager(metaclass=Singleton):

    def __init__(self) -> None:
        
        self.settings = Settings()
        self.settings.connect("proxy/uri", lambda *args: self.test_stability())

        self.providers: list[Booru] = [DanBooru()]
        self.test_stability()

    def test_stability(self) -> None:
        for provider in self.providers:
            provider.test_availability()

    def search_assets_by_tags_async(self, tags: list[str], callback: Callable[[Expected[set[Asset]]], Any]) -> Expected[set[Asset]]:

        tasks: list[Expected] = []

        def on_cancel() -> None:
            for task in tasks:
                task.cancel()

        e_assets: Expected[set[Asset]] = Expected(set(), on_cancel)

        def helper(_e_assets: Expected[set[Asset]]) -> None:
            e_assets.value |= _e_assets.value

            if all(task.is_finished() for task in tasks):
                e_assets.finish()
                callback(e_assets)

        for provider in self.providers:
            if not provider.is_alive: continue
            if e_assets.is_cancelled(): break
            tasks.append(provider.search_assets_by_tags_async(tags, helper))

        return e_assets