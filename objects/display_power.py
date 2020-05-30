#!/usr/bin/env python3

"""
        Module responsible for controlling the display power.
"""

import logging
import subprocess
import sys

from queue import Queue
from typing import Union

from events.event import Event
from events.event_control import EventControl
from events.signals import Signal
from objects.passive_object import PassiveObject

# Define the logger
LOG = logging.getLogger(__name__)


class DisplayPower(PassiveObject):
    """
    Class controlling the display power.
    """
    def __init__(self, communication_queue: Queue):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        """
        self.__communication_queue = communication_queue
        super().__init__()

    @staticmethod
    def __power_display(shall_power_on: bool) -> None:
        """
        Control the display power.
        :param shall_power_on: True if the display shall be powered on, False if it shall be powered off.
        :return: None
        """
        vcgencmd_call = ["vcgencmd", "display_power", "1" if shall_power_on else "0"]
        process = subprocess.Popen(vcgencmd_call, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                   universal_newlines=True)
        LOG.info("Display power switched %s.", "on" if shall_power_on else "off")
        process.wait()

        _, stderr = process.communicate()
        if stderr:
            LOG.error(stderr)

    def dispatch(self, event: Union[Event, EventControl]) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.signal() == Signal.DISPLAY_POWER_CONTROL:
            self.__power_display(event.enable())
        else:
            super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
