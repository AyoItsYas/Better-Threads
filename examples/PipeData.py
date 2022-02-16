import time
from BetterThreads import ThreadPool, Pipe

thread_pool, pipe = ThreadPool(), Pipe()


@thread_pool.thread()
def test_loop():
    data: int = pipe.recv()
    data += 1
    print(f"Loop running! data: {data}")
    time.sleep(1)
    pipe.send(data)


test_loop.start()
pipe.send(0)
print(f"Received! data: {pipe.recv()}")
test_loop.terminate()
