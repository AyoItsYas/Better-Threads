# Better Threads

A wrapper over threads that provides extended control. The module supports pausing, terminating and putting threads to sleep. The module also provides some additional tools to Pipe data between threads and a thread pool to keep track of threads.

## Key features
- Pipe data between threads
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


test_loop.start(test_loop)
time.sleep(5)
test_loop.terminate(test_loop)
```
