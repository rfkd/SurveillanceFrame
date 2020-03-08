#!/usr/bin/env python3

"""
        Module containing the camera motion event.
"""

import logging
import sys

from events.event import Event
from events.signals import Signal


class EventCameraMotion(Event):
    """
    Event to handle the camera motion detection.
    """
    def __init__(self, is_detected):
        """
        Class constructor.
        :param is_detected: True if motion has been detected, False otherwise.
        """
        self.__is_detected = is_detected
        super().__init__(Signal.CAMERA_MOTION)

    def is_detected(self):
        """
        Get the motion detection state.
        :return: True if motion has been detected, False otherwise.
        """
        return self.__is_detected


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
