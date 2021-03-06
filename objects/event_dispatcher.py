#!/usr/bin/env python3

"""
        Module responsible for dispatching events between objects.
"""

import logging
import sys
import time

from queue import Queue
from typing import List

from objects.passive_object import PassiveObject
from objects.threaded_object import ThreadedObject


class EventDispatcher(ThreadedObject):
    """
    Class dispatching events to objects. An event posted to the EventDispatcher queue will be dispatched to all assigned
    objects.
    """
    def __init__(self, communication_queue: Queue, objects: List[PassiveObject]):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param objects: List of objects to dispatch all received events to. Each object must have a dispatch() function.
        """
        self.__communication_queue = communication_queue
        self.__objects = objects
        super().__init__(self.__dispatch_events)

    def __dispatch_events(self) -> None:
        """
        Dispatch incoming events to assigned queues.
        :return: None
        """
        while self.shall_run():
            if self.__communication_queue.empty():
                time.sleep(0.1)
                continue

            event = self.__communication_queue.get()
            for element in self.__objects:
                element.dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
