#!/usr/bin/env python3

"""
        Module containing the base class for all threaded objects.
"""

from __future__ import annotations

import logging
import sys

from threading import Thread
from typing import Callable

from events.event import Event
from events.signals import Signal
from objects.passive_object import PassiveObject


class ThreadedObject(PassiveObject):
    """
    Base class for all threaded objects.
    """
    # Thread handle
    __thread_handle = None

    # Flag indicating whether the thread shall run
    __shall_run = False

    def __init__(self, thread_function: Callable):
        """
        Function to be started in a thread upon calling start().
        :param thread_function: Thread function.
        """
        self.__thread_function = thread_function

    def start(self) -> ThreadedObject:
        """
        Start the thread function.
        :return: Class instance.
        """
        self.__shall_run = True
        self.__thread_handle = Thread(target=self.__thread_function)
        self.__thread_handle.start()
        return self

    def stop(self) -> None:
        """
        Stop the thread.
        :return: None
        """
        self.__shall_run = False

    def join(self) -> None:
        """
        Wait until the thread has stopped.
        :return: None
        """
        self.__thread_handle.join()

    def shall_run(self) -> bool:
        """
        Get the expected running status of the thread.
        :return: True if the thread is supposed to run, False otherwise.
        """
        return self.__shall_run

    def is_running(self) -> bool:
        """
        Check if the thread is running.
        :return: True if the thread is running, False otherwise.
        """
        return self.__thread_handle.is_alive()

    def dispatch(self, event: Event) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return: None
        """
        if event.get_signal() == Signal.TERMINATE and self.__thread_handle.is_alive():
            self.__shall_run = False
            self.__thread_handle.join()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
