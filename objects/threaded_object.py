#!/usr/bin/env python3

"""
        Module containing the base class for all threaded objects.
"""

import logging
import sys

from threading import Thread

from events.signals import Signal


class ThreadedObject:
    """
    Base class for all threaded objects.
    """
    # Thread handle
    __thread_handle = None

    # Flag indicating whether the thread shall run
    __shall_run = False

    def __init__(self, thread_function):
        """
        Function to be started in a thread upon calling start().
        :param thread_function: Thread function.
        """
        self.__thread_function = thread_function

    def start(self):
        """
        Start the thread function.
        :return: Class instance
        """
        self.__shall_run = True
        self.__thread_handle = Thread(target=self.__thread_function)
        self.__thread_handle.start()
        return self

    def stop(self):
        """
        Stop the thread.
        :return: None
        """
        self.__shall_run = False

    def join(self):
        """
        Wait until the thread has stopped.
        :return: None
        """
        self.__thread_handle.join()

    def shall_run(self):
        """
        Get the expected running status of the thread.
        :return: True if the thread is supposed to run, False otherwise.
        """
        return self.__shall_run

    def is_running(self):
        """
        Check if the thread is running.
        :return: True if the thread is running, False otherwise.
        """
        return self.__thread_handle.is_alive()

    def dispatch(self, event):
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
