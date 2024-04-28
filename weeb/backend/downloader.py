# downloader.py
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
import httpx, hishel

from weeb.backend.utils.expected import Expected
from weeb.backend.utils.threading import run_in_thread
from weeb.backend.utils.singleton import Singleton

from weeb.backend.settings import Priority, Settings


class Downloader(metaclass=Singleton):

    def __init__(self) -> None:

        self.settings = Settings()

        self.settings.connect("proxy/uri", self.create_client, Priority.HIGH)

        self.create_client(self.settings.get("proxy/uri"))

    def create_client(self, proxy: str) -> None:

        controller = hishel.Controller(
            allow_heuristics=True,
            cacheable_status_codes=hishel.HEURISTICALLY_CACHEABLE_STATUS_CODES,
            allow_stale=True,
            always_revalidate=True
        )

        storage = hishel.FileStorage()
        limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
        transport = httpx.HTTPTransport(http1=False, http2=True, limits=limits, proxy=proxy)

        cache_transport = hishel.CacheTransport(transport=transport, storage=storage, controller=controller)
        
        self.client = httpx.Client(transport=cache_transport)

    def get(self, url: str, **kwargs) -> httpx.Response:
        try:
            return self.client.get(url, **kwargs)
        except httpx.HTTPError as e:
            return e.response

    def get_async(self, url: str, callback: Callable[[httpx.Response], Any], **kwargs) -> Expected[httpx.Response]:
        return run_in_thread(self.get, callback, url, **kwargs)

    def stream(self, url: str, method: str = "GET", **kwargs):
        try:
            return self.client.stream(method, url, **kwargs)
        except httpx.HTTPError as e:
            return e.response

    def stream_async(self, url: str, callback: Callable[[httpx.Response], Any], **kwargs) -> Expected[httpx.Response]:
        return run_in_thread(self.stream, callback, url, **kwargs)

    def download(self, url: str, stream = False, **kwargs) -> bytes | httpx.Response:
        if stream: return self.stream(url, **kwargs)
        else: return self.get(url, **kwargs).content
  
    def download_async(self, url: str, callback: Callable[[bytes], Any], stream = False, **kwargs) -> Expected[bytes]:

        e_bytes: Expected = None

        def helper(url: str, callback, **kwargs):
            with self.stream(url, **kwargs) as response:
                for chunk in response.iter_bytes():
                    callback(chunk)

        if stream: e_bytes = run_in_thread(helper, url, **kwargs)
        else: e_bytes = run_in_thread(self.download, callback, url, False, **kwargs)

        return e_bytes
        