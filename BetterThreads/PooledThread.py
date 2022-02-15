import time
from threading import Condition, Lock, Thread
from typing import Callable


class PooledThread(Thread):
    def __init__(self, target: Callable, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        self.__target: Callable = target

        self.__lock: Lock = Lock()

        self.__pause: bool = False
        self.__terminate: bool = False
        self.__sleep: bool = False
        self.__execution_event: Condition = Condition(self.__lock)

        super().__init__(target=self.control_wrapper)

    def is_asleep(self):
        return self.__sleep

    def is_paused(self):
        return self.__pause

    def is_alive(self):
        if self.__sleep or self.__pause: return False
        return super().is_alive()

    def pause(self, *, block: bool = True, timeout: int = None):
        with self.__lock: self.__pause = True

        if block: self.wait_cycle_execution(timeout=timeout)

    def resume(self):
        with self.__lock: self.__pause = False

    def sleep(self, seconds: int, *, block: bool = False, timeout: int = None):
        def dummy_thread():
            time.sleep(seconds)
            with self.__lock: self.__sleep = False

        with self.__lock: self.__sleep = True
        Thread(target=dummy_thread).start()

        if block: self.wait_cycle_execution(timeout=timeout)

    def terminate(self, *, block: bool = True, timeout: int = None):
        with self.__lock: self.__terminate = True

        if block: self.wait_cycle_execution(timeout=timeout)

    def wait_cycle_execution(self, *, timeout: int = None):
        """A blocking method that waits till the current thread cycle is over."""
        with self.__lock:
            self.__execution_event.wait(timeout=timeout)

    def control_wrapper(self):
        while not self.__terminate:
            self.__target(*self.__args, **self.__kwargs)
            with self.__lock: self.__execution_event.notify()
            while self.__pause or self.__sleep: pass
