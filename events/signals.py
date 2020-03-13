#!/usr/bin/env python3

"""
        Module containing all event signals used by the application.
"""

import logging
import sys

from enum import Enum


class Signal(Enum):
    """
    Class encapsulating all signals used in the application.
    """
    TERMINATE = 1
    BUTTON_PRESSED = 2
    CAMERA_MOTION_CHANGED = 3
    SENSOR_MOTION_CHANGED = 4
    CAMERA_STREAM_CONTROL = 5
    DISPLAY_POWER_CONTROL = 6
    SLIDESHOW_CONTROL = 7


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
