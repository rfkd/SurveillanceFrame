#!/usr/bin/env python3

"""
        Module responsible for displaying the surveillance camera stream.
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


class CameraStream(PassiveObject):
    """
    Class responsible for showing the camera stream.
    """
    # Process handle
    __process = None

    def __init__(self, communication_queue: Queue, stream_url: str):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param stream_url: URL of the camera stream.
        """
        self.__communication_queue = communication_queue
        self.__stream_url = stream_url
        super().__init__()

    def __start_stream(self) -> None:
        """
        Start the camera stream.
        :return: None
        """
        stream_call = ["omxplayer", "--avdict", "rtsp_transport:tcp", "--live", self.__stream_url]
        self.__process = subprocess.Popen(stream_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          universal_newlines=True)
        LOG.info("Camera stream has started.")

    def __stop_stream(self) -> None:
        """
        Stop the camera stream.
        :return: None
        """
        terminate_process(self.__process.pid)
        LOG.info("Camera stream has been stopped.")

    def dispatch(self, event: Union[Event, EventControl]) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.signal() == Signal.CAMERA_STREAM_CONTROL:
            if event.enable():
                if self.__process is None or self.__process.poll() is not None:
                    self.__start_stream()
            else:
                if self.__process is not None and self.__process.poll() is None:
                    self.__stop_stream()
        else:
            super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
