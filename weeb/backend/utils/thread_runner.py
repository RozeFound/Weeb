# thread_runner.py
#
# Copyright 2023 Adrian@death.andgravity.com
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
import contextlib
import sys
import threading
from typing import Any, Coroutine, Generator


class ThreadRunner:

    def __init__(self, *args, **kwargs) -> None:
        self._runner = asyncio.Runner(*args, **kwargs)
        self._thread = None
        self._stack = contextlib.ExitStack()

    def __enter__(self) -> "ThreadRunner":
        self._lazy_init()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        try:
            self._stack.close()
        finally:
            loop = self.get_loop()
            loop.call_soon_threadsafe(loop.stop)
            self._thread.join()

    def get_loop(self) -> None:
        self._lazy_init()
        return self._runner.get_loop()

    def run(self, coro: Coroutine) -> Any:
        loop = self.get_loop()
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    def _lazy_init(self) -> None:
        if self._thread:
            return

        loop_created = threading.Event()

        def run_forever():
            with self._runner as runner:
                loop = runner.get_loop()
                asyncio.set_event_loop(loop)
                loop_created.set()
                loop.run_forever()

        self._thread = threading.Thread(
            target=run_forever, name='LoopThread', daemon=True
        )
        self._thread.start()
        loop_created.wait()

    @contextlib.contextmanager
    def wrap_context(self, cm=None, factory=None) -> Generator[Any]:
        if cm is None:
            cm = self.run(call_async(factory))
        aenter = type(cm).__aenter__
        aexit = type(cm).__aexit__
        value = self.run(aenter(cm))
        try:
            yield value
        except:
            if not self.run(aexit(cm, *sys.exc_info())):
                raise
        else:
            self.run(aexit(cm, None, None, None))

    def enter_context(self, cm=None, factory=None) -> Any:
        cm = self.wrap_context(cm=cm, factory=factory)
        return self._stack.enter_context(cm)


async def call_async(callable):
    return callable()