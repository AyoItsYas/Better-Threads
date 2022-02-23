from __future__ import annotations

import time
from threading import Condition, Lock, Thread
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .ThreadPool import ThreadPool
    from .Pipe import Pipe


class SkipCycle(Exception): pass


class PooledThread(Thread):
    """A thread that can be paused, resumed and terminated."""
    def __init__(self, target: Callable, pool: ThreadPool, *, pipe: Pipe = None, name: str = None, args: tuple = tuple(), kwargs: dict = dict()):
        self.__args = args
        self.__kwargs = kwargs
        self.__pool: ThreadPool = pool
        self.__pipe: Pipe = pipe
        self.__target: Callable = target

        self.__lock: Lock = Lock()

        self.__pause: bool = False
        self.__terminate: bool = False
        self.__sleep: bool = False
        self.__execution_event: Condition = Condition(self.__lock)

        super().__init__(target=self.control_wrapper, name=name)

    def is_asleep(self):
        """Returns if the thread is sleeping or not."""
        return self.__sleep

    def is_paused(self):
        """Returns if the thread is paused or not."""
        return self.__pause

    def pause(self, *, block: bool = True, timeout: int = None):
        """Pause the execution of thread cycles."""
        with self.__lock: self.__pause = True

        if block: self.wait_cycle_execution(timeout=timeout)

    def resume(self, block: bool = True, timeout: int = None):
        """Resume the execution of thread cycles."""
        with self.__lock: self.__pause = False

        if block: self.wait_cycle_execution(timeout=timeout)

    def sleep(self, seconds: int, *, block: bool = False, timeout: int = None):
        """Pause the thread for a given amount of seconds."""
        def dummy_thread():
            time.sleep(seconds)
            with self.__lock: self.__sleep = False

        with self.__lock: self.__sleep = True
        Thread(target=dummy_thread).start()

        if block: self.wait_cycle_execution(timeout=timeout)

    def terminate(self, *, block: bool = True, timeout: int = None):
        """Terminate the thread once the cycle is finished."""
        with self.__lock: self.__terminate = True

        if block: self.wait_cycle_execution(timeout=timeout)

    def wait_cycle_execution(self, *, timeout: int = None):
        """A blocking method that waits till the current thread cycle is over."""
        with self.__lock:
            self.__execution_event.wait(timeout=timeout)

    def cycle_check(self):
        """A check to be called internally."""
        if self.__pause or self.__sleep or self.__terminate: raise SkipCycle("Cycle check failure!")

    def skip_cycle(self):
        """Raises an error to break the thread cycle."""
        raise SkipCycle

    def control_wrapper(self):
        """A simple function to wrap the original target around to gain control."""
        update = lambda: self.__pool.update(self)

        update()
        while not self.__terminate:
            try:
                result = self.__target(*self.__args, **self.__kwargs)  # Running the thread cycle
                if result: self.__pipe.send(result)
            except SkipCycle:  # An exception raised internally to terminate the cycle
                pass

            with self.__lock: self.__execution_event.notify()  # Notifing events waiting for cycle completion

            if self.__pause or self.__sleep:
                update()
                while self.__pause or self.__sleep: pass
                update()
        else:
            update()
            del self.__target, self.__args, self.__kwargs
