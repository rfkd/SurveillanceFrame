#!/usr/bin/env python3

"""
        Module responsible for watching a push button.
"""

import logging
import sys

from datetime import datetime
from queue import Queue

import RPi.GPIO as GPIO     # pylint: disable=import-error

from events.event_button_pressed import EventButtonPressed
from objects.passive_object import PassiveObject

# Define the logger
LOG = logging.getLogger(__name__)


class Button(PassiveObject):
    """
    Class handling a push button.
    """
    # Press types
    SHORT_PRESS = 1
    LONG_PRESS = 2

    # Minimum number of seconds the button has to be pressed for a long press.
    __LONG_PRESS_THRESHOLD = 1.5

    # Timestamp when the button has been pressed.
    __button_press_timestamp = None

    def __init__(self, communication_queue: Queue, gpio_channel: int):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param gpio_channel: GPIO BOARD channel number the button is connected to.
        """
        self.__communication_queue = communication_queue
        self.__gpio_channel = gpio_channel

        GPIO.setup(self.__gpio_channel, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
        GPIO.add_event_detect(self.__gpio_channel, GPIO.BOTH, callback=self.__button_state_change)
        LOG.info("Button initialized at GPIO %d.", self.__gpio_channel)

        super().__init__()

    def __button_state_change(self, gpio_channel: int) -> None:
        """
        Callback called when a button state has changed.
        :param gpio_channel: GPIO BOARD channel number which triggered the button state change.
        :return: None
        """
        assert gpio_channel == self.__gpio_channel

        if GPIO.input(self.__gpio_channel) == GPIO.HIGH:
            LOG.debug("Push button pressed.")
            self.__button_press_timestamp = datetime.now()
        else:
            button_press_time = datetime.now() - self.__button_press_timestamp
            button_press_time = button_press_time.seconds + button_press_time.microseconds / 1000000
            if button_press_time >= self.__LONG_PRESS_THRESHOLD:
                LOG.info("Long push button press detected.")
                self.__communication_queue.put(EventButtonPressed(self.LONG_PRESS))
            else:
                LOG.info("Short push button press detected.")
                self.__communication_queue.put(EventButtonPressed(self.SHORT_PRESS))


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
