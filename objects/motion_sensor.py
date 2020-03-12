#!/usr/bin/env python3

"""
        Module responsible for watching a motion sensor.
"""

import logging
import sys

from queue import Queue

import RPi.GPIO as GPIO     # pylint: disable=import-error

from events.event_motion import EventMotion
from events.signals import Signal
from objects.passive_object import PassiveObject

# Define the logger
LOG = logging.getLogger(__name__)


class MotionSensor(PassiveObject):
    """
    Class handling motion sensor detection.
    """
    def __init__(self, communication_queue: Queue, gpio_channel: int):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param gpio_channel: GPIO BOARD channel number the motion sensor is connected to.
        """
        self.__communication_queue = communication_queue
        self.__gpio_channel = gpio_channel

        GPIO.setup(self.__gpio_channel, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
        GPIO.add_event_detect(self.__gpio_channel, GPIO.BOTH, callback=self.__motion_detected)
        LOG.info("Motion sensor initialized at GPIO %d.", self.__gpio_channel)

    def __motion_detected(self, gpio_channel: int) -> None:
        """
        Callback called when a change in motion has been detected.
        :param gpio_channel: GPIO BOARD channel number which triggered the motion change.
        :return: None
        """
        assert gpio_channel == self.__gpio_channel

        if GPIO.input(self.__gpio_channel) == GPIO.HIGH:
            LOG.info("Motion has been detected.")
            self.__communication_queue.put(EventMotion(Signal.MOTION_SENSOR, True))
        else:
            LOG.info("Motion has ended.")
            self.__communication_queue.put(EventMotion(Signal.MOTION_SENSOR, False))


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
