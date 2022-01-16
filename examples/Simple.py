import time
from BetterThreads import ThreadPool

thread_pool = ThreadPool()


@thread_pool.thread()
def test_loop(data):
    print("Loop running!")
    time.sleep(1)


thread_pool.start(test_loop)
time.sleep(5)
thread_pool.stop(test_loop)
