import time
from BetterThreads import ThreadPool

thread_pool = ThreadPool()
data = {
    "something": "Data is sent from the MainThread",
    "some_other_thing": 0
}


def pipe_out(data: dict):
    """After the thread is done running it will return the passed data to a handler"""
    print(data)


pipe = ThreadPool.get_pipe(lambda: data, pipe_out)


@thread_pool.thread(pipe_in=pipe)
def test_loop(data: dict):
    print(f"Loop running! {data.get('iterations')}")
    time.sleep(1)


thread_pool.start(test_loop)
time.sleep(5)
thread_pool.stop(test_loop)
