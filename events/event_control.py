#!/usr/bin/env python3

"""
        Module containing the Control event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventControl(Event):
    """
    Event to control a receiver.
    """
    def __init__(self, signal: Signal, enable: bool):
        """
        Class constructor.
        :param signal: Signal of the event.
        :param enable: True if the receiver should be enabled, False if it should be disabled.
        """
        self.__enable = enable
        super().__init__(signal)

    def enable(self) -> bool:
        """
        Get the control state.
        :return: True if the receiver should be enabled, False if it should be disabled.
        """
        return self.__enable


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
