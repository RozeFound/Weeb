# danbooru.py
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
from typing import Callable

from httpx import Response

from weeb.backend.constants import debug
from weeb.backend.primitives import Asset, Booru, Variant
from weeb.backend.utils.expected import Expected


class DanBooru(Booru):

    def __init__(self) -> None:
        base_url = "https://testbooru.donmai.us" if debug else "https://danbooru.donmai.us"
        super().__init__(name="DanBooru", base_url=base_url)

        self.params = { "limit": 30 }

        if auth := self.settings.get(f"providers/{self.name}/auth"):
            login, api_key = auth.values()
            if login and api_key:
                self.params["login"] = login
                self.params["api_key"] = api_key

    def test_availability(self) -> Expected:

        params = { "limit": 1 }
        url = self.base_url + "/posts.json"

        def helper(result: Expected[Response]) -> None:
            if result.is_failed():
                self.is_alive = False
            else: self.is_alive = True

            logging.info(f"DanBooru is alive: {self.is_alive}")

        return self.downloader.get_async(url, helper, params=params, timeout=5.0)

    def parse_post(self, post: dict) -> Asset | None:

        media_asset = post.get("media_asset")
        variants: list[Variant] = []

        sample: Variant = None

        for variant in media_asset.get("variants", []):
            
            variants.append(Variant(
                width=variant.get("width"),
                height=variant.get("height"),
                url=variant.get("url")))

            if variant.get("type") == "sample":
                sample: Variant = variants[-1]

        if not variants: return None

        asset = Asset(
            id=media_asset.get("id"),
            hash=media_asset.get("md5"),
            variants=variants,
            preview=variants[0],
            sample=sample,
            original=variants[-1]
        )

        return asset
            
    def search_assets_async(self, tags: list, callback: Callable) -> Expected[set[Asset]]:

        e_assets: Expected[set] = Expected(set())

        def helper(e_response: Expected[Response]) -> None:

            response = e_response.value

            if response.status_code != 200:
                e_assets.error(response.text)
                return

            for post in response.json():
                asset = self.parse_post(post)
                if asset is None: continue
                e_assets.value.add(asset)

            e_assets.finish()
            callback(e_assets)
            
        
        self.params["tags"] = " ".join(tags)
        url = self.base_url + "/posts.json"

        self.downloader.get_async(url, helper, params=self.params)

        return e_assets