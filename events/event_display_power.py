#!/usr/bin/env python3

"""
        Module containing the display power event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventDisplayPower(Event):
    """
    Event to control the display power.
    """
    def __init__(self, shall_power_on: bool):
        """
        Class constructor.
        :param shall_power_on: True if the display shall power on, False if it shall power off.
        """
        self.__shall_power_on = shall_power_on
        super().__init__(Signal.DISPLAY_POWER)

    def shall_power_on(self) -> bool:
        """
        Get the desired display power state.
        :return: True if the display shall power on, False if it shall power off.
        """
        return self.__shall_power_on


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
