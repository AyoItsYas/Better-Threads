import time
from BetterThreads import ThreadPool

thread_pool = ThreadPool()


@thread_pool.thread()
def test_loop():
    print("Loop running!")
    time.sleep(1)


test_loop.start(test_loop)
time.sleep(5)
test_loop.terminate(test_loop)
