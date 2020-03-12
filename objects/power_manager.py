#!/usr/bin/env python3

"""
        Module responsible for power management.
"""

import datetime
import logging
import sys
import time

from queue import Queue
from typing import List, Optional

from events.event import Event
from objects.threaded_object import ThreadedObject

# Define the logger
LOG = logging.getLogger(__name__)


class PowerSchedule:
    """
    Class defining a power management schedule element.
    """
    def __init__(self, weekday: int, start: datetime.time, end: datetime.time, behavior: str):
        """
        Class constructor.
        :param weekday: Day of the week - 0: Monday, 1: Tuesday, ..., 6: Sunday.
        :param start: Start time (included).
        :param end: End time (included).
        :param behavior: Power behavior.
        """
        self.__weekday = weekday
        self.__start = start
        self.__end = end
        self.__behavior = behavior

    def __str__(self) -> str:
        """
        String representation of this object.
        :return: String representation.
        """
        return f"PowerSchedule(weekday={self.__weekday}, start={self.__start}, end={self.__end}, " \
               f"behavior={self.__behavior})"

    def weekday(self) -> int:
        """
        Get the weekday of the schedule.
        :return: Day of the week - 0: Monday, 1: Tuesday, ..., 6: Sunday.
        """
        return self.__weekday

    def start(self) -> datetime.time:
        """
        Get the start time (included).
        :return: Start time (included).
        """
        return self.__start

    def end(self) -> datetime.time:
        """
        Get the end time (included).
        :return: End time (included).
        """
        return self.__end

    def behavior(self) -> str:
        """
        Get the power behavior.
        :return: Power behavior.
        """
        return self.__behavior


class PowerManager(ThreadedObject):
    """
    Class responsible for power management.
    """
    class Behavior:
        """
        Class defining the power manager behavior types.
        """
        ALWAYS_ON = "ALWAYS_ON"
        MOTION_SENSOR = "MOTION_SENSOR"
        CAMERA_MOTION = "CAMERA_MOTION"

    # Currently active behavior
    __current_behavior = None

    def __init__(self, communication_queue: Queue, schedules: Optional[List[PowerSchedule]] = None):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param schedules: List of schedules or None.
        """
        self.__communication_queue = communication_queue

        self.__schedules = schedules
        if schedules:
            LOG.debug("Loaded power schedules:")
            for schedule in schedules:
                LOG.debug("* %s", schedule)
        else:
            LOG.debug("No schedules loaded.")

        super().__init__(self.__worker)

    def __get_current_behavior(self) -> str:
        """
        Get the current behavior based on the configured schedules. Defaults to "always on" if no schedule matches
        :return: Current behavior.
        """
        behavior = PowerManager.Behavior.ALWAYS_ON

        if self.__schedules:
            now = datetime.datetime.now()
            for schedule in self.__schedules:
                assert schedule.weekday() < 7
                assert schedule.start() < schedule.end()
                if schedule.weekday() == now.weekday() and schedule.start() <= now.time() <= schedule.end():
                    behavior = schedule.behavior()
                    break

        return behavior

    def __worker_always_on(self) -> None:
        """
        Worker function of the "always on" behavior:
        - Display: always powered on (power off with long button press, power back on with any button press)
        - Slideshow: always shown
        - Camera stream: shown upon camera motion detection or short button press (for 30 seconds)
        :return: None
        """
        # TODO Implement
        return

    def __worker_motion_sensor(self) -> None:
        """
        Worker function of the "motion sensor" behavior:
        - Display: powered on by the motion sensor (for 10 minutes)
        - Slideshow: always shown
        - Camera stream: shown upon camera motion detection or short button press (for 30 seconds)
        :return: None
        """
        # TODO Implement
        return

    def __worker_camera_motion(self) -> None:
        """
        Worker function of the "camera motion" behavior:
        - Display: powered on by camera motion (powered off when camera motion ends) or any button press
        - Slideshow: never shown
        - Camera stream: shown upon camera motion detection
        :return: None
        """
        # TODO Implement
        return

    def __worker(self) -> None:
        """
        Worker function of ther power manager.
        :return: None
        """
        LOG.info("Power manager has started.")

        while self.shall_run():
            # Check the current behavior based on the schedules
            current_behavior = self.__get_current_behavior()
            if current_behavior != self.__current_behavior:
                if self.__current_behavior is None:
                    LOG.info("Current behavior initialized as %s.", current_behavior)
                else:
                    LOG.info("Current behavior changed from %s to %s.", self.__current_behavior, current_behavior)
                self.__current_behavior = current_behavior

            # Power behavior
            if current_behavior == PowerManager.Behavior.ALWAYS_ON:
                self.__worker_always_on()
            elif current_behavior == PowerManager.Behavior.MOTION_SENSOR:
                self.__worker_motion_sensor()
            elif current_behavior == PowerManager.Behavior.CAMERA_MOTION:
                self.__worker_camera_motion()
            else:
                assert False

            # Let the CPU take a rest
            time.sleep(0.25)

        LOG.info("Power manager has stopped.")

    def dispatch(self, event: Event) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        # TODO Implement
        super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
