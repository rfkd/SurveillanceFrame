#!/usr/bin/env python3

"""
        Surveillance Frame main module.

        TODO:
        - Integrate power modes
        - Add motion sensor actions
        - Add push button actions
"""

import argparse
import logging
import re
import sys

from queue import Queue

import RPi.GPIO as GPIO     # pylint: disable=import-error

from events.event import Event
from events.signals import Signal
from objects.button import Button
from objects.camera_display import CameraDisplay
from objects.camera_motion import CameraMotion
from objects.display_power import DisplayPower
from objects.event_dispatcher import EventDispatcher
from objects.motion_sensor import MotionSensor
from objects.slideshow import Slideshow
from objects.threaded_object_supervisor import ThreadedObjectSupervisor

# Define the logger
LOG = logging.getLogger(__file__.split('.')[0])


def parse_arguments():
    """
    Parse the command line arguments.
    :return: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Surveillance frame application. By default the pictures shown in the "
                                                 "picture directory will be shown. When a '/?Message=start' GET "
                                                 "request has been received the stream URL will be shown until a "
                                                 "'/?Message=stop' GET request has been received.")
    parser.add_argument("-b", "--button-gpio", metavar="GPIO", action="store",
                        help="GPIO BOARD channel number a push button is connected to (active high)")
    parser.add_argument("-i", "--slideshow-interval", metavar="SECONDS", action="store", default=15,
                        help="time in seconds each picture will be shown (default: %(default)s)")
    parser.add_argument("-l", "--listen", metavar="IP:PORT", action="store", default="0.0.0.0:10042",
                        help="address to bind the HTTP motion trigger server to (default: %(default)s)")
    parser.add_argument("-m", "--motion-gpio", metavar="GPIO", action="store",
                        help="GPIO BOARD channel number a motion sensor is connected to (active high on motion)")
    parser.add_argument("-p", "--picture-dir", metavar="PATH", action="store",
                        help="path to the directory containing pictures to be shown when the camera is inactive")
    parser.add_argument("-s", "--stream-url", metavar="URL", action="store", required=True,
                        help="camera stream URL to be shown when motion is triggered")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    return parser.parse_args()


def configure_logging(arguments):
    """
    Configure logging.
    :param arguments: Parsed command line arguments.
    :return: None
    """
    if arguments.verbose:
        log_format = "%(asctime)s [%(levelname)s] <%(name)s> %(message)s"
        log_level = logging.DEBUG
    else:
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        log_level = logging.INFO
    logging.basicConfig(format=log_format, level=log_level)


def get_listen(listen):
    """
    Get the parsed --listen command line argument.
    :param listen: Value of the --listen command line argument.
    :return: Tuple consisting of IP and port to bind.
    """
    bind_ip = "0.0.0.0"

    result = re.match(r"^([0-9]+(?:\.[0-9]+){3}):([0-9]+)$", listen)
    if result:
        if result.group(1):
            bind_ip = result.group(1)
        bind_port = int(result.group(2))
    else:
        LOG.critical("Invalid IP/port specified.")
        sys.exit(-1)

    return bind_ip, bind_port


def main():
    """
    Main entry point.
    :return: None
    """
    # Application setup
    arguments = parse_arguments()
    configure_logging(arguments)
    bind_ip, bind_port = get_listen(arguments.listen)

    # GPIO mode
    GPIO.setmode(GPIO.BOARD)

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

        # Motion sensor
        if arguments.motion_gpio:
            motion_sensor = MotionSensor(communication_queue, arguments.motion_gpio)
            communication_objects.append(motion_sensor)

        # Button
        if arguments.button_gpio:
            button = Button(communication_queue, arguments.button_gpio)
            communication_objects.append(button)

        # Event dispatcher
        event_dispatcher = EventDispatcher(communication_queue, communication_objects).start()
        threaded_objects.append(event_dispatcher)

        # Threaded object supervisor
        threaded_object_supervisor = ThreadedObjectSupervisor(threaded_objects).start()
        threaded_object_supervisor.join()
    except KeyboardInterrupt:
        LOG.info("Received keyboard interrupt, shutting down...")
    finally:
        # Stop all objects
        if threaded_object_supervisor:
            threaded_object_supervisor.dispatch(Event(Signal.TERMINATE))

        # Configure the GPIOs to their previous state
        GPIO.cleanup()


if __name__ == "__main__":
    main()
