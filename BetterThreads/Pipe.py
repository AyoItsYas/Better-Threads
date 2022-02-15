import threading
from queue import Queue
from typing import Any


class Pipe:
    """A threadsafe passage to send data between threads."""
    def __init__(self):
        self.__queue = Queue(1)
        self.__lock = threading.Lock()
        self.__recv_check = threading.Condition(self.__lock)
        self.__send_check = threading.Condition(self.__lock)

    def send(self, value: Any):
        """Send data through the pipe."""
        with self.__send_check:
            while self.__queue.full():
                self.__send_check.wait()

            self.__queue.put(value)
            self.__recv_check.notify()

    def recv(self):
        """Receive data from the pipe."""
        with self.__recv_check:
            while self.__queue.empty():
                self.__recv_check.wait()

            value = self.__queue.get()
            self.__send_check.notify()

            return value
