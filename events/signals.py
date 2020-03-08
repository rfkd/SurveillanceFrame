#!/usr/bin/env python3

"""
        Module containing all event signals used by the application.
"""

import sys

from enum import Enum


class Signal(Enum):
    """
    Class encapsulating all signals used in the application.
    """
    TERMINATE = 1
    CAMERA_MOTION_START = 2
    CAMERA_MOTION_END = 3


if __name__ == "__main__":
    print("Error: Execute 'surveillance_frame.py' instead.", file=sys.stderr)
    sys.exit(-1)
