#!/usr/bin/env python3

"""
        Module responsible for watching a motion sensor.
"""

import logging
import sys


class PassiveObject:
    """
    Base class for all passive (i.e. non-threaded) objects.
    """
    # pylint: disable=no-self-use
    def dispatch(self, _):
        """
        Empty dispatch implementation needed by objects which only produce events but don't consume them.
        :return:
        """
        return


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
