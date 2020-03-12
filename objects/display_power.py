#!/usr/bin/env python3

"""
        Module responsible for controlling the display power.
"""

import logging
import subprocess
import sys

from queue import Queue

from events.event import Event
from events.signals import Signal

# Define the logger
LOG = logging.getLogger(__name__)


class DisplayPower:
    """
    Class controlling the display power.
    """

    def __init__(self, communication_queue: Queue, power_on_camera_motion: bool):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param power_on_camera_motion: Set True to control display power based on camera motion (enable power upon
                                       camera motion start, disable power upon camera motion stop).
        """
        self.__communication_queue = communication_queue
        self.__power_on_camera_motion = power_on_camera_motion

        if power_on_camera_motion:
            self.__power_display(False)

    @staticmethod
    def __power_display(shall_power_on: bool) -> None:
        """
        Control the display power.
        :param shall_power_on: True if the display shall be powered on, False if it shall be powered off.
        :return: None
        """
        # vcgencmd display_power0 / 1
        vcgencmd_call = [
            "vcgencmd",
            "display_power", "1" if shall_power_on else "0"
        ]

        process = subprocess.Popen(vcgencmd_call, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                   universal_newlines=True)
        LOG.info("Display power switched %s.", "on" if shall_power_on else "off")
        process.wait()

        _, stderr = process.communicate()
        if stderr:
            LOG.error(stderr)

    def dispatch(self, event: Event) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.get_signal() == Signal.DISPLAY_POWER:
            self.__power_display(event.shall_power_on())

        if self.__power_on_camera_motion and event.get_signal() == Signal.CAMERA_MOTION:
            self.__power_display(event.is_detected())


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
