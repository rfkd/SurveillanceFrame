#!/usr/bin/env python3

"""
        Module containing the Notify event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventNotify(Event):
    """
    Event to trigger a notification.
    """
    def __init__(self, text: str):
        """
        Class constructor.
        :param text: Notification text.
        """
        self.__text = text
        super().__init__(Signal.NOTIFY)

    def text(self) -> str:
        """
        Get the notification text.
        :return: Notification text.
        """
        return self.__text


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
