#!/usr/bin/env python3

"""
        Surveillance Frame main module.
"""

import argparse
import datetime
import logging
import os
import re
import signal
import sys

from logging.handlers import TimedRotatingFileHandler
from queue import Queue
from typing import List, Optional, Tuple

import RPi.GPIO as GPIO     # pylint: disable=import-error

from events.event import Event
from events.signals import Signal
from objects.button import Button
from objects.camera_stream import CameraStream
from objects.camera_motion import CameraMotion
from objects.display_power import DisplayPower
from objects.event_dispatcher import EventDispatcher
from objects.motion_sensor import MotionSensor
from objects.notifier import Notifier
from objects.power_manager import PowerManager, PowerSchedule
from objects.slideshow import Slideshow
from objects.threaded_object_supervisor import ThreadedObjectSupervisor

# Define the logger
LOG = logging.getLogger(os.path.basename(__file__).split('.')[0])


def parse_arguments() -> argparse.Namespace:
    """
    Parse the command line arguments.
    :return: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Surveillance frame application controlling a picture slideshow, display power\n"
                    "and a surveillance camera stream. The behavior of the application is configured\n"
                    "by (multiple) power mode schedules.\n\n"
                    "The following power modes are available:\n"
                    "- ALWAYS_ON:     Display is always on but can be powered off with a long button\n"
                    "                 press (power back on with any button press).\n"
                    "- CAMERA_MOTION: Display is off unless the camera detected motion. A short\n"
                    "                 button press enables the display and shows the camera stream\n"
                    "                 for 30 seconds.\n"
                    "- MOTION_SENSOR: Display is off but will be switched on for 'motion-timeout'\n"
                    "                 seconds if the motion sensor detected motion (timer is\n"
                    "                 restarted upon further motion). It will also be switched on while\n"
                    "                 the camera detects motion. A short button press enables the\n"
                    "                 display and shows the camera stream for 60 seconds.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-b", "--button-gpio", metavar="GPIO", action="store",
                        help="GPIO BOARD channel number a push button is connected to (active high)")
    parser.add_argument("-i", "--slideshow-interval", metavar="SECONDS", action="store", default=15,
                        help="time in seconds each picture will be shown (default: %(default)s)")
    parser.add_argument("-l", "--listen", metavar="IP:PORT", action="store", default="0.0.0.0:10042",
                        help="address to bind the HTTP motion trigger server to (default: %(default)s)")
    parser.add_argument("-L", "--log-file", action="store", help="log to the given file (rotated at midnight)")
    parser.add_argument("-m", "--motion-gpio", metavar="GPIO", action="store",
                        help="GPIO BOARD channel number a motion sensor is connected to (active high on motion)")
    parser.add_argument("-p", "--picture-dir", metavar="PATH", action="store",
                        help="path to the directory containing pictures to be shown")
    parser.add_argument("-s", "--stream-url", metavar="URL", action="store", required=True,
                        help="camera stream URL to be shown")
    parser.add_argument("-S", "--schedule", action="store", nargs="+",
                        help="power mode schedule in the format: <weekday>,<start>,<end>,<mode>\n"
                             " <weekday>: day of the week (Monday, Tuesday, ...), 'weekday' (Monday until\n"
                             "            Friday), 'weekend' (Saturday and Sunday) or 'anyday' (Monday until\n"
                             "            Sunday)\n"
                             " <start>: start time in the format HH:MM\n"
                             " <end>: end time (not included) in the format HH:MM\n"
                             " <mode>: power mode, see above\n"
                             "Example: Tuesday,22:00,0:00,CAMERA_MOTION\n"
                             "Default mode if no schedule matches is ALWAYS_ON. First matching schedule will\n"
                             "be used.")
    parser.add_argument("-t", "--motion-timeout", metavar="SECONDS", action="store", default=3600,
                        help="timeout for which the display will be switched on when motion has been detected (default:"
                             " %(default)s)")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose logging")
    return parser.parse_args()


def configure_logging(arguments: argparse.Namespace) -> None:
    """
    Configure logging.
    :param arguments: Parsed command line arguments.
    :return: None
    """
    if arguments.verbose:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] <%(name)s> %(message)s")
        level = logging.DEBUG
    else:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Log to console
    console_log = logging.StreamHandler()
    console_log.setLevel(level)
    console_log.setFormatter(formatter)
    root_logger.addHandler(console_log)

    # Log to file
    if arguments.log_file:
        file_log = TimedRotatingFileHandler(arguments.log_file, when="midnight", backupCount=13)
        file_log.setLevel(level)
        file_log.setFormatter(formatter)
        root_logger.addHandler(file_log)


def get_listen(listen: str) -> Tuple[str, int]:
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


def get_schedules(schedules: List[str]) -> Optional[List[PowerSchedule]]:
    """
    Get a list of power schedules from the given command line arguments.
    :param schedules:
    :return:
    """
    if schedules is None:
        return None

    power_schedules = []
    for schedule in schedules:
        elements = schedule.split(",")
        if len(elements) != 4:
            LOG.critical("Invalid power schedule '%s' given.", schedule)
            sys.exit(-1)

        # Weekday
        weekdays = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
                    "weekday": PowerSchedule.WEEKDAY, "weekend": PowerSchedule.WEEKEND, "anyday": PowerSchedule.ANYDAY}
        try:
            weekday = weekdays[elements[0].lower()]
        except KeyError:
            LOG.critical("Invalid weekday '%s' given.", elements[0])
            sys.exit(-1)

        # Start time
        time_pattern = r"^(\d{1,2}):(\d{2})$"
        result = re.match(time_pattern, elements[1])
        if result:
            start = datetime.time(int(result.group(1)), int(result.group(2)), 0)
        else:
            LOG.critical("Invalid start time '%s' given.", elements[1])
            sys.exit(-1)

        # End time
        result = re.match(time_pattern, elements[2])
        if result:
            end = datetime.time(int(result.group(1)), int(result.group(2)), 0)
            if end != datetime.time(0) and start >= end:
                LOG.critical("End time '%s' must be after start time.", elements[2])
                sys.exit(-1)
        else:
            LOG.critical("Invalid end time '%s' given.", elements[2])
            sys.exit(-1)

        # Power mode
        modes = {"ALWAYS_ON": PowerManager.Mode.ALWAYS_ON, "CAMERA_MOTION": PowerManager.Mode.CAMERA_MOTION,
                 "MOTION_SENSOR": PowerManager.Mode.MOTION_SENSOR}
        try:
            mode = modes[elements[3].upper()]
        except KeyError:
            LOG.critical("Invalid power mode '%s' given.", elements[3])
            sys.exit(-1)

        # Argument is valid, add the power schedule
        power_schedules.append(PowerSchedule(weekday, start, end, mode))

    return power_schedules


def signal_handler(signal_number: int, _) -> None:
    """
    Signal handler.
    :param signal_number: Signal number.
    :param _: Stack frame.
    :return: None
    :raise: OSError with signal string.
    """
    # pylint: disable=no-member
    raise OSError(signal.Signals(signal_number).name)


# pylint: disable=too-many-locals
def main() -> None:
    """
    Main entry point.
    :return: None
    """
    # Application setup
    arguments = parse_arguments()
    configure_logging(arguments)
    bind_ip, bind_port = get_listen(arguments.listen)
    schedules = get_schedules(arguments.schedule)
    signal.signal(signal.SIGTERM, signal_handler)

    # GPIO mode
    GPIO.setmode(GPIO.BOARD)

    # Start the application
    threaded_object_supervisor = None
    threaded_objects = []
    try:
        communication_objects = []
        communication_queue = Queue()

        # Display power
        display_power = DisplayPower(communication_queue)
        communication_objects.append(display_power)

        # Slideshow
        if arguments.picture_dir:
            slideshow = Slideshow(communication_queue, arguments.picture_dir, int(arguments.slideshow_interval))
            communication_objects.append(slideshow)

        # Camera stream
        camera_stream = CameraStream(communication_queue, arguments.stream_url)
        communication_objects.append(camera_stream)

        # Camera motion
        camera_motion = CameraMotion(communication_queue, bind_ip, bind_port).start()
        communication_objects.append(camera_motion)
        threaded_objects.append(camera_motion)

        # Motion sensor
        if arguments.motion_gpio:
            motion_sensor = MotionSensor(communication_queue, int(arguments.motion_gpio))
            communication_objects.append(motion_sensor)

        # Button
        if arguments.button_gpio:
            button = Button(communication_queue, int(arguments.button_gpio))
            communication_objects.append(button)

        # Power manager
        power_manager = PowerManager(communication_queue, int(arguments.motion_timeout), schedules).start()
        communication_objects.append(power_manager)
        threaded_objects.append(power_manager)

        # Notifier
        notifier = Notifier(communication_queue).start()
        communication_objects.append(notifier)
        threaded_objects.append(notifier)

        # Event dispatcher
        event_dispatcher = EventDispatcher(communication_queue, communication_objects).start()
        threaded_objects.append(event_dispatcher)

        # Threaded object supervisor
        threaded_object_supervisor = ThreadedObjectSupervisor(threaded_objects).start()
        threaded_object_supervisor.join()
    except KeyboardInterrupt:
        LOG.info("Received keyboard interrupt, shutting down...")
    except OSError as exception:
        LOG.info("Received %s, shutting down...", exception)
    finally:
        # Stop all objects
        if threaded_object_supervisor:
            threaded_object_supervisor.dispatch(Event(Signal.TERMINATE))

        # Configure the GPIOs to their previous state
        GPIO.cleanup()


if __name__ == "__main__":
    main()
