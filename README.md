# Better Threads
Ever wanted to pause, stop, resume or pipe data between threads? Well this module does exactly that.

## Key features
- Pass data between threads
- Pause, Resume and Stop threads
- Simple
## Installing
**Python 3.7 or higher is required**
```
pip install better-threads
```
## Quick example
More exmples https://github.com/ItsYasiru/Better-Threads/tree/master/examples
```py
import time
from BetterThreads import ThreadPool

thread_pool = ThreadPool()


@thread_pool.thread()
def test_loop():
    print("Loop running!")
    time.sleep(1)


thread_pool.start(test_loop)
time.sleep(5)
thread_pool.pause(test_loop)
time.sleep(5)
thread_pool.resume(test_loop)
time.sleep(5)
thread_pool.stop(test_loop)
```
