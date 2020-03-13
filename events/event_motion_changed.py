#!/usr/bin/env python3

"""
        Module containing the MotionChanged event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventMotionChanged(Event):
    """
    Event to indicate motion.
    """
    def __init__(self, signal: Signal, motion: bool):
        """
        Class constructor.
        :param signal: Signal of the event.
        :param motion: True if motion is active, False otherwise.
        """
        self.__motion = motion
        super().__init__(signal)

    def motion(self) -> bool:
        """
        Get the motion state.
        :return: True if motion is active, False otherwise.
        """
        return self.__motion


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
