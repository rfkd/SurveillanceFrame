#!/usr/bin/env python3

"""
        Module containing miscellaneous functions.
"""

import logging
import sys

import psutil

# Define the logger
LOG = logging.getLogger(__name__)


def terminate_process(pid: int) -> None:
    """
    Terminate the process tree with the given PID.
    :param pid: PID to terminate.
    :return: None
    """
    parent = psutil.Process(pid)

    # Terminate child processes
    children = parent.children(recursive=True)
    for child in children:
        child.terminate()
    _, alive = psutil.wait_procs(children, timeout=3)
    for child in alive:
        LOG.warning("Child process of PID %d was stopped forcefully.", pid)
        child.kill()

    # Terminate parent process
    parent.terminate()
    try:
        parent.wait(3)
    except psutil.TimeoutExpired:
        LOG.warning("Parent process with PID %d was stopped forcefully.", pid)
        parent.kill()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
