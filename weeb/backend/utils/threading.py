# threading.py
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

from typing import Callable, Optional
import threading, functools, traceback

from weeb.backend.utils.expected import Expected

from gi.repository import GLib

class GThread(threading.Thread):
    """A Thread class that can be used in GTK+ applications to run functions in a background thread"""

    def __init__(self, target: Callable, result: Expected, callback: Optional[Callable] = None, *args, **kwargs) -> None:

        def handler(*args, **kwargs) -> None:
            try: result.value = target(*args, **kwargs)
            except Exception as e: 
                traceback.print_exception(e)
                result.set_error(e)
                result.fail()

            if not result.is_cancelled() and not result.is_failed():
                result.finish()

            if callback and not result.is_cancelled():
                callback(result)

        super().__init__(target=handler, args=args, kwargs=kwargs, daemon=True)

        self.start()


def run_in_thread(target: Callable,  callback: Optional[Callable] = None, *args, **kwargs) -> Expected:

    result = Expected()
    GThread(target, result, callback, *args, **kwargs)
    return result

def glib_idle(func: Callable) -> Callable:
    """Wraps a function in a GLib.idle_add() call"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs: args += tuple([value for _, value in kwargs])
        GLib.idle_add(func, *args)

    return wrapper