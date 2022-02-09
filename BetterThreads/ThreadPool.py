import threading
import time

from typing import Callable

from errors import TimeOut


class ThreadPool:
    def __init__(self) -> None:
        self.threads: dict[str, dict] = dict()

    def __len__(self) -> int:
        return len(self.threads)

    def start(self, func: Callable = None, *, thread_id: str = None):
        """Starts the thread"""
        thread_data = self.get_thread(func, thread_id=thread_id)
        if thread_data:
            thread_data["thread"].start()

    def terminate(self, func: Callable = None, *, thread_id: str = None):
        """Terminates a running thread"""
        thread_data = self.get_thread(func, thread_id=thread_id)
        if thread_data:
            thread_data["data"]["terminate"] = True

    def pause(self, func: Callable = None, *, thread_id: str = None, resume_in: int = None):
        """Pause a running thread"""
        def resume_dummy():
            time.sleep(resume_in)
            self.resume(func)

        thread_data = self.get_thread(func, thread_id=thread_id)
        if thread_data:
            thread_data["data"]["pause"] = True

        if resume_in:
            threading.Thread(target=resume_dummy).start()

    def resume(self, func: Callable = None, *, thread_id: str = None):
        """Resume a paused thread"""
        thread_data = self.get_thread(func, thread_id=thread_id)
        if thread_data:
            thread_data["data"]["pause"] = False

    def terminate_all(self, *, wait: bool = None, timeout: int = None):
        """Terminates all running threads"""
        threads = self.threads.copy()

        for thread_id, thread in threads.items():
            thread["data"]["terminate"] = True
            self.threads.pop(thread_id)

        if wait:
            start = time.time()
            while any(thread_data["thread"].is_alive() for thread_data in threads.values()):
                if timeout:
                    if time.time() - start > timeout:
                        raise TimeOut()

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
        """A function decorator. Add a function to the pool"""
        def wrap(func):
            self.add_thread(func, *args, **kwargs)
            return func
        return wrap

    def add_thread(self, func: Callable, *args, **kwargs):
        """Add a function to the pool"""
        data = {
            "pause": False,
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
