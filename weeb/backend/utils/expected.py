# expected.py
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

import enum
from typing import Callable, Generic, Optional, TypeVar


class Status(enum.Enum):
    FINISHED = "finished"
    CANCELLED = "cancelled"
    RUNNING = "running"
    FAILED = "failed"


T = TypeVar('T')
class Expected(Generic[T]):

    def __init__(self, value: Optional[T] = None, on_cancel: Optional[Callable] = None, on_fail: Optional[Callable] = None,  on_finish: Optional[Callable] = None) -> None:

        self.__on_cancel_cb = on_cancel
        self.__on_fail_cb = on_fail
        self.__on_finish_cb = on_finish

        self.__error = None
        self.__value = value

        self.__status = Status.RUNNING

    def cancel(self) -> None:
        self.__status = Status.CANCELLED
        self.on_cancel()

    def fail(self) -> None:
        self.__status = Status.FAILED
        self.on_fail()

    def finish(self) -> None:
        self.__status = Status.FINISHED
        self.on_finish()

    @property
    def status(self) -> Status:
        return self.__status

    def is_running(self) -> bool:
        return self.__status == Status.RUNNING

    def is_finished(self) -> bool:
        return self.__status == Status.FINISHED

    def is_cancelled(self) -> bool:
        return self.__status == Status.CANCELLED

    def is_failed(self) -> bool:
        return self.__status == Status.FAILED

    @property
    def value(self) -> T:
        return self.__value

    @value.setter
    def value(self, value: T) -> None:
        self.__value = value

    def get_error(self) -> Optional[Exception]:
        return self.__error

    def set_error(self, error: Exception) -> None:
        self.__error = error

    @property
    def on_cancel(self) -> Callable:

        if self.__on_cancel_cb is None:
            return lambda *args, **kwargs: None

        return self.__on_cancel_cb

    @property
    def on_fail(self) -> Callable:

        if self.__on_fail_cb is None:
            return lambda *args, **kwargs: None

        return self.__on_fail_cb

    @property
    def on_finish(self) -> Callable:

        if self.__on_finish_cb is None:
            return lambda *args, **kwargs: None

        return self.__on_finish_cb

    def set_on_cancel(self, on_cancel: Callable) -> None:
        self.__on_cancel_cb = on_cancel

    def set_on_fail(self, on_fail: Callable) -> None:
        self.__on_fail_cb = on_fail

    def set_on_finish(self, on_finish: Callable) -> None:
        self.__on_finish_cb = on_finish
