#!/usr/bin/env python3

"""
        Module responsible for showing the picture slideshow.
"""

import logging
import subprocess
import sys

from queue import Queue
from typing import Union

from events.event import Event
from events.event_control import EventControl
from events.signals import Signal
from miscellaneous.miscellaneous import terminate_process
from objects.passive_object import PassiveObject

# Define the logger
LOG = logging.getLogger(__name__)


class Slideshow(PassiveObject):
    """
    Class handling the picture slideshow.
    """
    # Process handle
    __process = None

    def __init__(self, communication_queue: Queue, picture_dir: str, slideshow_interval: int):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param picture_dir: Path to the directory containing the pictures to be shown.
        :param slideshow_interval: Interval between two pictures.
        """
        self.__communication_queue = communication_queue
        self.__picture_dir = picture_dir
        self.__slideshow_interval = slideshow_interval
        super().__init__()

    def __start_slideshow(self) -> None:
        """
        Start the slideshow.
        :return: None
        """
        slideshow_call = ["feh", "--quiet", "--fullscreen", "--hide-pointer", "--recursive", f"{self.__picture_dir}",
                          "--slideshow-delay", f"{self.__slideshow_interval}", "--reload", "10"]
        self.__process = subprocess.Popen(slideshow_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          universal_newlines=True)
        LOG.info("Slideshow has started in directory %s with an interval of %d seconds.",
                 self.__picture_dir, self.__slideshow_interval)

    def __stop_slideshow(self) -> None:
        """
        Stop the slideshow.
        :return: None
        """
        terminate_process(self.__process.pid)
        LOG.info("Slideshow has been stopped.")

    def dispatch(self, event: Union[Event, EventControl]) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.signal() == Signal.SLIDESHOW_CONTROL:
            if event.enable():
                if self.__process is None or self.__process.poll() is not None:
                    self.__start_slideshow()
            else:
                if self.__process is not None and self.__process.poll() is None:
                    self.__stop_slideshow()
        else:
            super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
