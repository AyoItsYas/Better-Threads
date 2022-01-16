import time
import BetterThreads
from BetterThreads import ThreadPool

thread_pool = BetterThreads.ThreadPool()


def afterthis(data: dict):
    print(data)


data = {
    "spotted": 0,
    "pause": False,
    "terminate": False
}
pipe = ThreadPool.get_pipe(lambda: data, afterthis)


@thread_pool.thread(pipe_in=pipe, pipe_out=afterthis)
def dothis(*, data: dict = None):
    print("Worker running!")
    time.sleep(1)

    data["spotted"] += 1

    if data:
        return data


thread_pool.start(thread_id="0")
time.sleep(3)
thread_pool.pause_all(resume_in=3)
time.sleep(3)
thread_pool.stop_all()
