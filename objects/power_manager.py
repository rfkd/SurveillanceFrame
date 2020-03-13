#!/usr/bin/env python3

"""
        Module responsible for power management.
"""

import datetime
import logging
import sys
import time

from queue import Queue
from typing import List, Optional, Union

from events.event import Event
from events.event_button_pressed import EventButtonPressed
from events.event_control import EventControl
from events.event_motion_changed import EventMotionChanged
from events.signals import Signal
from miscellaneous.timer import Timer
from objects.button import Button
from objects.threaded_object import ThreadedObject

# Define the logger
LOG = logging.getLogger(__name__)


class PowerSchedule:
    """
    Class defining a power management schedule element.
    """
    def __init__(self, weekday: int, start: datetime.time, end: datetime.time, mode: str):
        """
        Class constructor.
        :param weekday: Day of the week - 0: Monday, 1: Tuesday, ..., 6: Sunday.
        :param start: Start time (included).
        :param end: End time (included).
        :param mode: Power mode.
        """
        self.__weekday = weekday
        self.__start = start
        self.__end = end
        self.__mode = mode

    def __str__(self) -> str:
        """
        String representation of this object.
        :return: String representation.
        """
        return f"PowerSchedule(weekday={self.__weekday}, start={self.__start}, end={self.__end}, mode={self.__mode})"

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

    def mode(self) -> str:
        """
        Get the power mode.
        :return: Power mode.
        """
        return self.__mode


class PowerManager(ThreadedObject):
    """
    Class responsible for power management.
    """
    class Mode:
        """
        Class defining the power manager mode types.
        """
        ALWAYS_ON = "ALWAYS_ON"
        MOTION_SENSOR = "MOTION_SENSOR"
        CAMERA_MOTION = "CAMERA_MOTION"

    # Currently active mode
    __current_mode = None

    # Input states
    __in_button_press = None
    __in_camera_motion = False
    __in_sensor_motion = False

    # Output states
    __out_camera_stream = False
    __out_display_power = False
    __out_slideshow = False

    # Timer
    __timer = Timer()

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

    def __get_current_mode(self) -> str:
        """
        Get the current mode based on the configured schedules. Defaults to "always on" if no schedule matches
        :return: Current mode.
        """
        mode = PowerManager.Mode.ALWAYS_ON

        if self.__schedules:
            now = datetime.datetime.now()
            for schedule in self.__schedules:
                assert schedule.weekday() < 7
                assert schedule.start() < schedule.end()
                if schedule.weekday() == now.weekday() and schedule.start() <= now.time() <= schedule.end():
                    mode = schedule.mode()
                    break

        return mode

    def __control_display_power(self, enable: bool) -> None:
        """
        Control the display power.
        :param enable: True to enable, False to disable.
        :return: None
        """
        self.__communication_queue.put(EventControl(Signal.DISPLAY_POWER_CONTROL, enable))
        self.__out_display_power = enable

    def __control_slideshow(self, enable: bool) -> None:
        """
        Control the slideshow.
        :param enable: True to enable, False to disable.
        :return: None
        """
        self.__communication_queue.put(EventControl(Signal.SLIDESHOW_CONTROL, enable))
        self.__out_slideshow = enable

    def __control_camera_stream(self, enable: bool) -> None:
        """
        Control the camera stream.
        :param enable: True to enable, False to disable.
        :return: None
        """
        self.__communication_queue.put(EventControl(Signal.CAMERA_STREAM_CONTROL, enable))
        self.__out_camera_stream = enable

    def __worker_always_on(self, initialize: bool) -> None:
        """
        Worker function of the "always on" mode:
         - Display: always powered on (power off with long button press, power back on with any button press)
         - Slideshow: always shown
         - Camera stream: shown upon camera motion detection or short button press (for 30 seconds)
        :param initialize: Set True to initialize the mode.
        :return: None
        """
        if initialize:
            self.__timer.stop()
            self.__control_display_power(True)
            self.__control_slideshow(True)

        # Display power
        if self.__out_display_power:
            if self.__in_button_press == Button.LONG_PRESS:
                self.__control_display_power(False)
        else:
            if self.__in_button_press is not None:
                self.__control_display_power(True)
            else:
                # Do nothing if the display is off
                return

        # Camera display
        if self.__out_camera_stream:
            if not self.__in_camera_motion and self.__timer.is_expired():
                self.__control_camera_stream(False)
        else:
            if self.__in_camera_motion:
                self.__control_camera_stream(True)
            elif self.__in_button_press == Button.SHORT_PRESS:
                self.__control_camera_stream(True)
                self.__timer.start(30)

        # Reset a pressed button
        self.__in_button_press = None

    def __worker_motion_sensor(self, initialize: bool) -> None:
        """
        Worker function of the "motion sensor" mode:
         - Display: powered on by the motion sensor (for 10 minutes)
         - Slideshow: always shown
         - Camera stream: shown upon camera motion detection or short button press (for 30 seconds)
        :param initialize: Set True to initialize the mode.
        :return: None
        """
        # TODO Implement
        return

    def __worker_camera_motion(self, initialize: bool) -> None:
        """
        Worker function of the "camera motion" mode:
         - Display: powered on by camera motion (powered off when camera motion ends) or any button press
         - Slideshow: never shown
         - Camera stream: shown upon camera motion detection
        :param initialize: Set True to initialize the mode.
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
            # Check the current mode based on the schedules
            current_mode = self.__get_current_mode()
            initialize_worker = False
            if current_mode != self.__current_mode:
                initialize_worker = True
                if self.__current_mode is None:
                    LOG.info("Current mode initialized as %s.", current_mode)
                else:
                    LOG.info("Current mode changed from %s to %s.", self.__current_mode, current_mode)
                self.__current_mode = current_mode

            # Power mode
            if current_mode == PowerManager.Mode.ALWAYS_ON:
                self.__worker_always_on(initialize_worker)
            elif current_mode == PowerManager.Mode.MOTION_SENSOR:
                self.__worker_motion_sensor(initialize_worker)
            elif current_mode == PowerManager.Mode.CAMERA_MOTION:
                self.__worker_camera_motion(initialize_worker)
            else:
                assert False

            # Let the CPU take a rest
            time.sleep(0.25)

        LOG.info("Power manager has stopped.")

    def dispatch(self, event: Union[Event, EventButtonPressed, EventMotionChanged]) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.signal() == Signal.BUTTON_PRESSED:
            self.__in_button_press = event.press_type()
        elif event.signal() == Signal.CAMERA_MOTION_CHANGED:
            self.__in_camera_motion = event.motion()
        elif event.signal() == Signal.SENSOR_MOTION_CHANGED:
            self.__in_sensor_motion = event.motion()
        else:
            super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
