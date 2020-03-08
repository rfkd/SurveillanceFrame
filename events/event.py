#!/usr/bin/env python3

"""
        Module containing the base class for all events.
"""

import logging
import sys


class Event:
    """
    Base class for all events.
    """
    def __init__(self, signal):
        """
        Class constructor.
        :param signal: Signal used by this event.
        """
        self.signal = signal

    def __str__(self):
        """
        String representation of this object.
        :return: String representation.
        """
        return f"Event({self.signal})"


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
