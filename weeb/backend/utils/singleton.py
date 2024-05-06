#All credits to https://stackoverflow.com/a/71174451

import threading
from typing import Any, Dict


class Singleton(type):
    _instances = {}
    _singleton_locks: Dict[Any, threading.Lock] = {}

    def __call__(cls, *args, **kwargs):
        """
        Create and return an instance of the class. 

        This method implements the singleton design pattern, ensuring that only one instance of the class is created.

        Parameters:
            cls (type): The class object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            object: The instance of the class.

        Note:
            This method uses the double-checked locking pattern to ensure thread safety.
        """
        # double-checked locking pattern (https://en.wikipedia.org/wiki/Double-checked_locking)
        if cls not in cls._instances:
            if cls not in cls._singleton_locks:
                cls._singleton_locks[cls] = threading.Lock()
            with cls._singleton_locks[cls]:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]