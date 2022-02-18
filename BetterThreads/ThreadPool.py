import time
from threading import Thread, Lock
from typing import Callable, Union

from BetterThreads.PooledThread import PooledThread


class ThreadPool:
    def __init__(self):
        """A simple thread manager."""
        self.__lock: Lock = Lock()
        self.__threads: dict[Callable, PooledThread] = dict()
        self.__dead_threads: dict[Callable, PooledThread] = dict()

    def __len__(self):
        self._update()
        return len(self.__threads)

    @property
    def threads(self):
        """Number of threads in the pool."""
        self._update()
        return len(self)

    def _update(self):
        """Updates internal variables keeping track of threads in the pool."""
        threads = self.__threads.copy()
        for func, thread in threads.items():
            if not thread.is_alive():
                with self.__lock: self.__dead_threads[func] = self.__threads.pop(func)

        dead_threads = self.__dead_threads.copy()
        for func, thread in dead_threads.items():
            if thread.is_alive():
                with self.__lock: self.__threads[func] = self.__dead_threads.pop(func)

    def thread(self):
        """Function decorator to easily add a function as a thread to the pool."""
        def wrapper(func: Union[Callable, PooledThread], *args, **kwargs):
            return self.add_thread(func, *args, **kwargs)
        return wrapper

    def add_thread(self, func: Union[Callable, PooledThread], *args, **kwargs):
        """Add a function as a thread to the pool."""
        with self.__lock:
            if isinstance(func, PooledThread):
                self.__threads[func._PooledThread__target] = func
            else:
                thread = PooledThread(func, *args, **kwargs)
                self.__threads[func] = thread
                return thread

    def terminate(self, func: Union[Callable, PooledThread] = None, block: bool = None, timeout: int = None):
        thread = self.get_thread(func)

        if thread:
            thread.terminate(block=block, timeout=timeout)
            with self.__lock: del self.__threads[func]
            self._update()

    def terminate_all(self, *, block: bool = True, timeout: int = None):
        """Terminates all threads in the pool"""
        for thread in self.__threads.values():
            thread.terminate(block=False)
        self._update()

        if block:
            start = time.time()
            while any(thread.is_alive() for thread in self.__threads.values()):
                if timeout:
                    if time.time() - start > timeout: break
            with self.__lock: self.__threads = dict()

    def pause(self, func: Union[Callable, PooledThread] = None, *, resume_in: int = None, block: bool = True, timeout: int = None):
        def resume_dummy():
            time.sleep(resume_in)
            thread.resume()

        thread = self.get_thread(func)

        if thread:
            if resume_in:
                Thread(target=resume_dummy).start()
            thread.pause(block=block, timeout=timeout)
            self._update()

    def pause_all(self, *, resume_in: int = None, block: bool = True, timeout: int = None):
        """Pause all the threads in the pool"""
        def dummy_thread():
            time.sleep(resume_in)
            self.resume_all(block=False)

        self._update()
        for thread in self.__threads.values():
            thread.pause(block=False)

        if resume_in: Thread(target=dummy_thread).start()

        if block:
            start = time.time()
            while any(not thread.is_paused() for thread in self.__threads.values()):
                if timeout:
                    if time.time() - start > timeout: break
        self._update()

    def resume(self, func: Union[Callable, PooledThread] = None):
        thread = self.get_thread(func)

        if thread: thread.resume()
        self._update()

    def resume_all(self, *, block: bool = True):
        """Resume all the threads in the pool"""
        self._update()
        for thread in self.__dead_threads.values():
            thread.resume(block=False)

        if block:
            while any(thread.is_paused() for thread in self.__threads.values()): pass
        self._update()

    def get_thread(self, func: Union[Callable, PooledThread] = None, checks: list = list(), check: Callable = None) -> Union[PooledThread, None]:
        """Get the `Thread` object from a function."""
        self._update()
        if check: checks.append(check)
        for thread in self.__threads.values() + self.__dead_threads.values():
            if func == thread._PooledThread__target: return thread
            if any(_(func, thread) for _ in checks): return thread
