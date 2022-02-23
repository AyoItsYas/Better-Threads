import time
from threading import Lock, Thread
from typing import Callable, Union

from BetterThreads.PooledThread import PooledThread


class ThreadPool:
    def __init__(self):
        """A simple thread manager."""
        self.__lock: Lock = Lock()
        self.__threads: list[PooledThread] = list()

    def __len__(self):
        """Number of threads in the pool."""
        self.update()
        return len(self.__threads)

    @property
    def threads(self):
        """Number of threads in the pool."""
        return len(self.__threads)

    def update(self, thread: PooledThread = None):
        """Updates internal variables keeping track of threads in the pool."""
        if thread:
            if not thread.is_alive():
                with self.__lock: self.__threads.remove(thread)
        else:
            for thread in self.__threads.copy():
                if not thread.is_alive():
                    with self.__lock: self.__threads.remove(thread)

    def thread(self, *args, **kwargs):
        """Function decorator to easily add a function as a thread to the pool."""
        def wrapper(func: Union[Callable, PooledThread]):
            return self.add_thread(func, *args, **kwargs)
        return wrapper

    def add_thread(self, func: Union[Callable, PooledThread], *args, **kwargs) -> Union[None, PooledThread]:
        """Add a function as a thread to the pool."""
        thread = func if isinstance(func, PooledThread) else PooledThread(func, self, *args, **kwargs)
        with self.__lock: self.__threads.append(thread)
        return thread

    def get_thread(
        self,
        func: Union[Callable, PooledThread] = None,
        checks: list[Callable[[Callable, PooledThread], bool]] = list(),
        check: Callable[[Callable, PooledThread], bool] = None
    ) -> Union[None, PooledThread]:
        """Get the `Thread` object from a function."""
        if check: checks.append(check)
        for thread in self.__threads:
            if func == thread._PooledThread__target: return thread
            if any(check(func, thread) for check in checks): return thread

    def terminate(self, func: Union[Callable, PooledThread] = None, block: bool = None, timeout: int = None):
        thread = self.get_thread(func)

        if thread:
            thread.terminate(block=block, timeout=timeout)
            with self.__lock: del self.__threads[func]

    def terminate_all(self, *, block: bool = True, timeout: int = None):
        """Terminates all threads in the pool"""
        def check(thread: PooledThread):
            if thread.is_asleep() or thread.is_paused():
                return False

        for thread in self.__threads:
            thread.terminate()

        if block:
            start = time.time()
            while any(check(thread) for thread in self.__threads):
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

    def pause_all(self, *, resume_in: int = None, block: bool = True, timeout: int = None):
        """Pause all the threads in the pool"""
        def dummy_thread():
            time.sleep(resume_in)
            self.resume_all(block=False)

        for thread in self.__threads:
            thread.pause(block=False)

        if resume_in: Thread(target=dummy_thread).start()

        if block:
            start = time.time()
            while any(not thread.is_paused() for thread in self.__threads):
                if timeout:
                    if time.time() - start > timeout: break

    def resume(self, func: Union[Callable, PooledThread] = None):
        thread = self.get_thread(func)

        if thread: thread.resume()

    def resume_all(self, *, block: bool = True):
        """Resume all the threads in the pool"""
        for thread in self.__threads:
            thread.resume()

        if block:
            while any(thread.is_paused() for thread in self.__threads): pass
