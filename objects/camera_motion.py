#!/usr/bin/env python3

"""
        Module responsible for handling incoming camera motion HTTP requests.
"""

import logging
import socketserver
import sys

from queue import Queue
from http.server import BaseHTTPRequestHandler

from events.event import Event
from events.event_motion_changed import EventMotionChanged
from events.signals import Signal
from objects.threaded_object import ThreadedObject

# Define the logger
LOG = logging.getLogger(__name__)


class CameraMotion(ThreadedObject):
    """
    Class handling camera motion detection.
    """
    # HTTP server handle.
    __httpd = None

    def __init__(self, communication_queue: Queue, bind_ip: str, bind_port: int):
        """
        Class constructor.
        :param communication_queue: Queue used for event communication.
        :param bind_ip: IP to bind the HTTP server to.
        :param bind_port: Port to bind the HTTP server to.
        """
        self.__communication_queue = communication_queue
        self.__bind_ip = bind_ip
        self.__bind_port = bind_port
        super().__init__(self.__start_httpd)

    class RequestHandler(BaseHTTPRequestHandler):
        """
        HTTP request handler class.
        """
        def do_GET(self) -> None:   # pylint: disable=invalid-name
            """
            Handle GET requests.
            :return: None
            """
            http_response = 200

            # Simulation example: curl -X GET http://localhost:10042/?Message=start
            if self.path == "/?Message=start":
                LOG.info("Client %s indicated motion start.", self.client_address[0])
                self.server.communication_queue.put(EventMotionChanged(Signal.CAMERA_MOTION_CHANGED, True))
            elif self.path == "/?Message=stop":
                LOG.info("Client %s indicated motion end.", self.client_address[0])
                self.server.communication_queue.put(EventMotionChanged(Signal.CAMERA_MOTION_CHANGED, False))
            else:
                LOG.warning("Client %s sent unknown request: %s", self.client_address[0], self.path)
                http_response = 400

            self.send_response(http_response)
            self.end_headers()

        def log_message(self, _, *args: str) -> None:
            """
            Disable logging.
            """
            return

    def __start_httpd(self) -> None:
        """
        Start the HTTP server.
        :return: None
        """
        socketserver.TCPServer.allow_reuse_address = True
        socketserver.TCPServer.logging = False
        self.__httpd = socketserver.TCPServer((self.__bind_ip, self.__bind_port), CameraMotion.RequestHandler)
        self.__httpd.communication_queue = self.__communication_queue

        LOG.info("Starting HTTP server on %s:%d.", self.__bind_ip, self.__bind_port)
        self.__httpd.serve_forever()
        LOG.info("HTTP server has stopped.")

    def dispatch(self, event: Event) -> None:
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return None
        """
        if event.signal() == Signal.TERMINATE and self.is_running() and self.__httpd:
            self.__httpd.shutdown()
            self.__httpd.server_close()
        super().dispatch(event)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.critical("This module cannot be executed.")
    sys.exit(-1)
