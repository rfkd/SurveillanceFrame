#!/usr/bin/env python3

"""
        Module containing the ButtonPressed event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventButtonPressed(Event):
    """
    Event to indicate changed button states.
    """
    def __init__(self, press_type: int):
        """
        Class constructor.
        :param press_type: Button press type.
        """
        self.__press_type = press_type
        super().__init__(Signal.BUTTON_PRESSED)

    def press_type(self) -> int:
        """
        Get the button press type.
        :return: Button press type.
        """
        return self.__press_type


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
