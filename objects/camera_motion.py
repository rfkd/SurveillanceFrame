#!/usr/bin/env python3

"""
        Module responsible for handling incoming camera motion HTTP requests.
"""

import socketserver
import sys

from http.server import BaseHTTPRequestHandler

from events.event import Event
from events.signals import Signal
from objects.threaded_object import ThreadedObject


class CameraMotion(ThreadedObject):
    """
    Class handling camera motion detection.
    """
    # HTTP server handle.
    __httpd = None

    def __init__(self, communication_queue, bind_ip, bind_port):
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
        def do_GET(self):   # pylint: disable=invalid-name
            """
            Handle GET requests.
            :return: None
            """
            http_response = 200

            if self.path == "/?Message=start":
                print(f"Motion triggered by {self.client_address[0]}")
                self.server.communication_queue.put(Event(Signal.CAMERA_MOTION_START))
            elif self.path == "/?Message=stop":
                print(f"Motion end triggered by {self.client_address[0]}")
                self.server.communication_queue.put(Event(Signal.CAMERA_MOTION_END))
            else:
                print(f"Unknown request received from {self.client_address[0]}: {self.path}")
                http_response = 400

            self.send_response(http_response)
            self.end_headers()

        def log_message(self, _, *args):
            """
            Disable logging.
            """
            return

    def __start_httpd(self):
        """
        Start the HTTP server.
        :return: None
        """
        socketserver.TCPServer.allow_reuse_address = True
        socketserver.TCPServer.logging = False
        self.__httpd = socketserver.TCPServer((self.__bind_ip, self.__bind_port), CameraMotion.RequestHandler)
        self.__httpd.communication_queue = self.__communication_queue

        print(f"Starting HTTP server on {self.__bind_ip}:{self.__bind_port}.")
        self.__httpd.serve_forever()
        print("HTTP server has stopped.")

    def dispatch(self, event):
        """
        Dispatch the given event to the object.
        :param event: Event to be dispatched.
        :return
        """
        if event.signal == Signal.TERMINATE and self.is_running() and self.__httpd:
            self.__httpd.shutdown()
            self.__httpd.server_close()
        super().dispatch(event)


if __name__ == "__main__":
    print("Error: Execute 'surveillance_frame.py' instead.", file=sys.stderr)
    sys.exit(-1)
