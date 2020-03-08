#!/usr/bin/env python3

"""
        Module responsible for supervising all threaded objects.
"""

import logging
import sys
import time

from events.event import Event
from events.signals import Signal
from objects.threaded_object import ThreadedObject


class ThreadedObjectSupervisor(ThreadedObject):
    """
    Class supervising other threaded objects.
    """
    def __init__(self, threaded_objects):
        """
        Class constructor.
        :param threaded_objects: List of threaded objects to be supervised.
        """
        self.__threaded_objects = threaded_objects
        super().__init__(self.__supervise_threaded_objects)

    def __supervise_threaded_objects(self):
        """
        Supervise threaded objects. In case one of the supervised threads stops all other objects will be stopped as
        well.
        :return: None
        """
        while self.shall_run():
            # Abort if one of the threads is not running anymore
            for threaded_object in self.__threaded_objects:
                if not threaded_object.is_running():
                    self.stop()

            # Let the CPU take some rest
            time.sleep(0.5)

        # Stop all threaded objects
        for threaded_object in self.__threaded_objects:
            threaded_object.dispatch(Event(Signal.TERMINATE))


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
