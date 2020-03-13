#!/usr/bin/env python3

"""
        Module containing the Timer class.
"""

import logging
import sys
import time


class Timer:
    """
    Class defining a timer.
    """
    def __init__(self):
        """
        Class constructor.
        """
        self.__seconds = 0
        self.__start_time = 0

    def start(self, seconds: int) -> None:
        """
        Start the timer.
        :param seconds: Number of seconds to arm the timer with.
        :return: None
        """
        self.__seconds = seconds
        self.__start_time = time.time()

    def stop(self) -> None:
        """
        Stop the timer.
        :return: None
        """
        self.__seconds = 0
        self.__start_time = 0

    def is_expired(self) -> bool:
        """
        Check if the timer hasn't started or is expired.
        :return: True if the timer hasn't started or is expired, False otherwise.
        """
        if self.__start_time == 0 or self.__seconds == 0:
            return True

        return time.time() > self.__start_time + self.__seconds


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
