#!/usr/bin/env python3

"""
        Surveillance Frame main module.

        TODO:
        - Switch off HDMI when unused
        - Add motion sensor support
        - Add push button support
"""

import argparse
import logging
import re
import sys

from queue import Queue

from events.event import Event
from events.signals import Signal
from objects.camera_display import CameraDisplay
from objects.camera_motion import CameraMotion
from objects.display_power import DisplayPower
from objects.event_dispatcher import EventDispatcher
from objects.slideshow import Slideshow
from objects.threaded_object_supervisor import ThreadedObjectSupervisor

# Define the logger
LOG = logging.getLogger(__file__.split('.')[0])


# pylint: disable=too-many-locals
def main():
    """
    Main entry point.
    :return: None
    """
    # Command line arguments
    parser = argparse.ArgumentParser(description="Surveillance frame application. By default the pictures shown in the "
                                                 "picture directory will be shown. When a '/?Message=start' GET "
                                                 "request has been received the stream URL will be shown until a "
                                                 "'/?Message=stop' GET request has been received.")
    parser.add_argument("-i", "--slideshow-interval", metavar="SECONDS", action="store", default=15,
                        help="time in seconds each picture will be shown (default: %(default)s)")
    parser.add_argument("-l", "--listen", metavar="IP:PORT", action="store", default="0.0.0.0:10042",
                        help="address to bind the HTTP motion trigger server to (default: %(default)s)")
    parser.add_argument("-p", "--picture-dir", metavar="PATH", action="store",
                        help="path to the directory containing pictures to be shown when the camera is inactive")
    parser.add_argument("-s", "--stream-url", metavar="URL", action="store", required=True,
                        help="camera stream URL to be shown when motion is triggered")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    arguments = parser.parse_args()

    # Configure logging
    if arguments.verbose:
        log_format = "%(asctime)s [%(levelname)s] <%(name)s> %(message)s"
        log_level = logging.DEBUG
    else:
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        log_level = logging.INFO
    logging.basicConfig(format=log_format, level=log_level)

    # Validate command line arguments
    bind_ip = "0.0.0.0"
    result = re.match(r"^([0-9]+(?:\.[0-9]+){3}):([0-9]+)$", arguments.listen)
    if result:
        if result.group(1):
            bind_ip = result.group(1)
        bind_port = int(result.group(2))
    else:
        LOG.critical("Invalid IP/port specified.")
        sys.exit(-1)

    # Start the application
    threaded_object_supervisor = None
    threaded_objects = []
    try:
        communication_objects = []
        communication_queue = Queue()

        # Display power
        display_power_object = DisplayPower(communication_queue, arguments.picture_dir is None)
        communication_objects.append(display_power_object)

        # Slideshow
        if arguments.picture_dir:
            slideshow_object = Slideshow(communication_queue, arguments.picture_dir,
                                         arguments.slideshow_interval).start()
            communication_objects.append(slideshow_object)
            threaded_objects.append(slideshow_object)

        # Camera display
        camera_display_object = CameraDisplay(communication_queue, arguments.stream_url,
                                              arguments.picture_dir is not None)
        communication_objects.append(camera_display_object)

        # Camera motion
        camera_motion_object = CameraMotion(communication_queue, bind_ip, bind_port).start()
        communication_objects.append(camera_motion_object)
        threaded_objects.append(camera_motion_object)

        # Event dispatcher
        event_dispatcher = EventDispatcher(communication_queue, communication_objects).start()
        threaded_objects.append(event_dispatcher)

        # Threaded object supervisor
        threaded_object_supervisor = ThreadedObjectSupervisor(threaded_objects).start()
        threaded_object_supervisor.join()
    except KeyboardInterrupt:
        LOG.info("Received keyboard interrupt, shutting down...")
    finally:
        if threaded_object_supervisor:
            threaded_object_supervisor.dispatch(Event(Signal.TERMINATE))


if __name__ == "__main__":
    main()
