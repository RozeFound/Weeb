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

import asyncio
from functools import partial
from typing import Optional
import httpx, hishel, xxhash

from httpcore import Request
from hishel._utils import generate_key

from weeb.backend.utils.thread_runner import ThreadRunner

class Downloader:

    def __init__(self) -> None:
        
        self.runner = ThreadRunner()
        factory = partial(httpx.AsyncClient, transport=get_cache_transport())
        self.client: httpx.AsyncClient = self.runner.enter_context(factory=factory)

    def close(self) -> None:
        self.runner.close()

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        return await self.client.get(url, **kwargs)

    async def _get_many(self, urls: list[str], **kwargs) -> list[httpx.Response]:
        futures = [self._get(url, **kwargs) for url in urls]
        return await asyncio.gather(*futures)

    def get(self, urls: str | list[str], **kwargs) -> httpx.Response | list[httpx.Response]:
        if isinstance(urls, str):
            return self.runner.run(self._get(urls, **kwargs))
        return self.runner.run(self._get_many(urls, **kwargs))


def get_cache_transport(proxy: Optional[httpx.Proxy] = None) -> hishel.AsyncCacheTransport:

    def key_generator(request: Request, body: bytes = b"") -> str:
        key = generate_key(request, body, xxhash.xxh3_64)
        
        method = request.method.decode()
        host = request.url.host.decode()
        return f"{method}|{host}|{key}"

    controller = hishel.Controller(
        allow_heuristics=True,
        cacheable_status_codes=hishel.HEURISTICALLY_CACHEABLE_STATUS_CODES,
        allow_stale=True,
        always_revalidate=True,
        key_generator=key_generator
    )

    storage = hishel.AsyncFileStorage()
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    transport = httpx.AsyncHTTPTransport(http1=False, http2=True, limits=limits, proxy=proxy)

    return hishel.AsyncCacheTransport(transport=transport, storage=storage, controller=controller)