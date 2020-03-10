#!/usr/bin/env python3

"""
        Module containing the button press event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventButtonPress(Event):
    """
    Event to signal button presses.
    """
    # Press types
    SHORT_PRESS = 0
    LONG_PRESS = 1

    def __init__(self, press_type):
        """
        Class constructor.
        :param press_type: Button press type.
        """
        self.__press_type = press_type
        super().__init__(Signal.BUTTON_PRESS)

    def get_press_type(self):
        """
        Get the button press type.
        :return: Button press type.
        """
        return self.__press_type


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
