# Better Threads
Ever wanted to pause, stop, resume ot pipe data between threads? This python module extends control over threads. Example usage,
```py
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
```
More exmples https://github.com/ItsYasiru/Better-Threads/examples