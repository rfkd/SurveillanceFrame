#!/usr/bin/env python3

"""
        Module responsible for showing notifications.
"""

import logging
import subprocess
import sys
import time

from queue import Queue
from shutil import which
from typing import Union

from events.event import Event
from events.event_notify import EventNotify
from events.signals import Signal
from objects.threaded_object import ThreadedObject

# Define the logger
LOG = logging.getLogger(__name__)


class Notifier(ThreadedObject):
    """
    Class handling on-screen notifications.
    """
    # Notification text
    __text = None

    def __init__(self, communication_queue: Queue):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        """
        self.__communication_queue = communication_queue
        super().__init__(self.__show_notification)

    def __show_notification(self) -> None:
        """
        Show received notifications.
        :return: None
        """
        LOG.info("Notifier has started.")

        while self.shall_run():
            if self.__text:
                if which("aosd_cat") is not None:
                    LOG.debug("Notification: %s", self.__text)

                    aosd_cat_call = ["aosd_cat", "--fore-color", "white", "--font", "Helvetica 20", "--position", "8",
                                     "--x-offset", "-50", "--fade-in", "100", "--fade-full", "1000"]
                    subprocess.run(aosd_cat_call, input=self.__text, check=False, universal_newlines=True)
                else:
                    LOG.warning("Cannot show notification '%s', aosd_cat is unavailable.", self.__text)

                self.__text = None

            # Let the CPU take a rest
            time.sleep(0.25)

        LOG.info("Notifier has stopped.")

    def dispatch(self, event: Union[Event, EventNotify]) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.signal() == Signal.NOTIFY:
            self.__text = event.text()
        else:
            super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
