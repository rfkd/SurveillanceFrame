#!/usr/bin/env python3

"""
        Module responsible for dispatching events between objects.
"""

import sys
import time

from objects.threaded_object import ThreadedObject


class EventDispatcher(ThreadedObject):
    """
    Class dispatching events to objects. An event posted to the EventDispatcher queue will be dispatched to all assigned
    objects.
    """
    def __init__(self, communication_queue, objects):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param objects: List of objects to dispatch all received events to. Each object must have a dispatch() function.
        """
        self.__communication_queue = communication_queue
        self.__objects = objects
        super().__init__(self.__dispatch_events)

    def __dispatch_events(self):
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
    print("Error: Execute 'surveillance_frame.py' instead.", file=sys.stderr)
    sys.exit(-1)
