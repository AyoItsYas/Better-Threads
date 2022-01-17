import time
from BetterThreads import ThreadPool

thread_pool = ThreadPool()

data = {
    "count": 0
}
pipe = thread_pool.get_pipe(lambda: data)


@thread_pool.thread()
def test_loop():
    data = pipe()
    data["count"] += 1
    print(f"Loop running! {data.get('count')}")
    time.sleep(1)


thread_pool.start(test_loop)
time.sleep(5)
thread_pool.stop(test_loop)
print(data)
