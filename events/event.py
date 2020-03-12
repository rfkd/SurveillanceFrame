#!/usr/bin/env python3

"""
        Module containing the base class for all events.
"""

import logging
import sys

from events.signals import Signal


class Event:
    """
    Base class for all events.
    """
    def __init__(self, signal: Signal):
        """
        Class constructor.
        :param signal: Signal used by this event.
        """
        self.__signal = signal

    def __str__(self) -> str:
        """
        String representation of this object.
        :return: String representation.
        """
        return f"Event({self.__signal})"

    def get_signal(self) -> Signal:
        """
        Get the signal of the event.
        :return: Event signal
        """
        return self.__signal


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
