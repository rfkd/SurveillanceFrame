#!/usr/bin/env python3

"""
        Module responsible for showing the picture slideshow.
"""

import logging
import subprocess
import sys
import time

from objects.threaded_object import ThreadedObject

# Define the logger
LOG = logging.getLogger(__name__)


class Slideshow(ThreadedObject):
    """
    Class handling the picture slideshow.
    """
    def __init__(self, communication_queue, picture_dir, slideshow_interval):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param picture_dir: Path to the directory containing the pictures to be shown.
        :param slideshow_interval: Interval between two pictures.
        """
        self.__communication_queue = communication_queue
        self.__picture_dir = picture_dir
        self.__slideshow_interval = slideshow_interval
        super().__init__(self.__slideshow)

    def __slideshow(self):
        """
        Start the slideshow.
        :return: None
        """
        slideshow_call = [
            "feh",
            "--quiet",
            "--fullscreen",
            "--hide-pointer",
            "--recursive", f"{self.__picture_dir}",
            "--slideshow-delay", f"{self.__slideshow_interval}"
        ]

        process = subprocess.Popen(slideshow_call, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                   universal_newlines=True)
        LOG.info("Slideshow has started in directory %s with an interval of %d seconds.",
                 self.__picture_dir, self.__slideshow_interval)
        while self.shall_run() and not process.poll():
            time.sleep(1)

        if process.returncode:
            _, stderr = process.communicate()
            print(stderr, file=sys.stderr)

        LOG.info("Slideshow has stopped.")


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
