import threading
import time
from typing import Callable


class ThreadPool:
    def __init__(self) -> None:
        self.threads: dict[str, dict] = dict()

    def start(self, func: Callable = None, *, thread_id: str = None):
        """Starts the thread"""
        x = self.get_thread(func, thread_id=thread_id)
        if x:
            x["thread"].start()

    def stop(self, func: Callable = None, *, thread_id: str = None):
        """Stops a running thread"""
        x = self.get_thread(func, thread_id=thread_id)
        if x:
            x["data"]["terminate"] = True

    def pause(self, func: Callable = None, *, thread_id: str = None, resume_in: int = None):
        """Pause a thread"""
        def resume_dummy():
            time.sleep(resume_in)
            self.resume(func)

        x = self.get_thread(func, thread_id=thread_id)
        if x:
            x["data"]["pause"] = True

        if resume_in:
            threading.Thread(target=resume_dummy).start()

    def resume(self, func: Callable = None, *, thread_id: str = None):
        """Resume a paused thread"""
        x = self.get_thread(func, thread_id=thread_id)
        if x:
            x["data"]["pause"] = False

    def stop_all(self, *, wait: bool = None, timeout: int = None):
        """Stops all threads in the pool"""
        threads = self.threads.copy()

        for thread_id, thread in threads.items():
            thread["data"]["terminate"] = True
            self.threads.pop(thread_id)

        if wait:
            start = time.time()
            while any(x["thread"].is_alive() for x in threads.values()):
                if timeout:
                    if time.time() - start > timeout:
                        raise Exception("Timeout")

    def pause_all(self, *, resume_in: int = None):
        """Pause all the threads in the pool"""
        def resume_dummy():
            time.sleep(resume_in)
            self.resume_all()

        for thread in self.threads.values():
            thread["data"]["pause"] = True

        if resume_in:
            threading.Thread(target=resume_dummy).start()

    def resume_all(self):
        """Resume all the threads in the pool"""
        for thread in self.threads.values():
            thread["data"]["pause"] = False

    def thread(self, *args, **kwargs):
        """A function Decorator. Calls the given function on each thread cycle."""
        def wrap(func):
            data = {
                "iterations": 0,
                "terminate": False
            }
            pipe = self.get_pipe(lambda: data)

            def worker(pipe):
                def pipe_in(key: str = None):
                    if key:
                        data: dict = pipe()
                        data = data.get(key, None)
                        if hasattr(data, '__call__'):
                            return data()
                        else:
                            return data
                    else:
                        return pipe()

                def pipe_out(data, *, finished: bool = None):
                    return pipe(data, finished=finished)

                while not pipe_in("terminate"):
                    while pipe_in("pause") and not pipe_in("terminate"):
                        pass
                    if pipe_in("terminate"):
                        break

                    func(*args, **kwargs)

            thread = threading.Thread(target=worker, args=(pipe,))
            thread_id = self.get_id()

            self.threads[thread_id] = {
                "data": data,
                "func": func,
                "thread": thread
            }
            return func
        return wrap

    def get_id(self) -> int:
        return str(len(self.threads))

    def get_thread(self, func: Callable = None, *, thread_id: str = None):
        if func is not None:
            for thread_id, thread in self.threads.items():
                if func == thread["func"]:
                    return thread
        return self.threads.get(thread_id)

    @staticmethod
    def get_pipe(pipe_in: Callable, pipe_out: Callable = lambda data: None):
        """Builds a pipe function to pipe data between the main thread and the thread"""
        def pipe(data: dict = None, *, finished: bool = None):
            if data and finished:
                return pipe_out(data)
            elif data:
                pipe_in().update(data)
                return pipe_in()
            else:
                return pipe_in()
        return pipe
