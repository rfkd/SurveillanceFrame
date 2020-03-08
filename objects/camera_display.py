#!/usr/bin/env python3

"""
        Module responsible for displaying the surveillance camera stream.
"""

import subprocess
import sys

import psutil

from events.signals import Signal


class CameraDisplay:
    """
    Class responsible for showing the camera stream.
    """
    # Process handle
    __process = None

    def __init__(self, communication_queue, stream_url):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param stream_url: URL of the camera stream.
        """
        self.__communication_queue = communication_queue
        self.__stream_url = stream_url

    def __start_stream(self):
        """
        Start the camera stream.
        :return: None
        """
        stream_call = [
            "omxplayer",
            "--avdict", "rtsp_transport:tcp",
            "--live",
            self.__stream_url
        ]

        self.__process = subprocess.Popen(stream_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          universal_newlines=True)
        print("Stream has started")

    def __stop_stream(self):
        """
        Stop the camera stream.
        :return: None
        """
        parent = psutil.Process(self.__process.pid)

        # Terminate child processes
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        _, alive = psutil.wait_procs(children, timeout=3)
        for child in alive:
            child.kill()

        # Terminate parent process
        parent.terminate()
        try:
            parent.wait(3)
        except psutil.TimeoutExpired:
            parent.kill()

    def dispatch(self, event):
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return
        """
        if event.signal == Signal.CAMERA_MOTION_START:
            if self.__process is None or self.__process.poll() is not None:
                self.__start_stream()
            return

        if event.signal == Signal.CAMERA_MOTION_END:
            if self.__process is not None and self.__process.poll() is None:
                self.__stop_stream()
            return


if __name__ == "__main__":
    print("Error: Execute 'surveillance_frame.py' instead.", file=sys.stderr)
    sys.exit(-1)
