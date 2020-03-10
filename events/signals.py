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
    CAMERA_MOTION = 2
    DISPLAY_POWER = 3
    MOTION_SENSOR = 4
    BUTTON_PRESS = 5


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
