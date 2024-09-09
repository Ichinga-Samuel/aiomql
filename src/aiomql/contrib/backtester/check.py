import signal
import asyncio
from asyncio import Condition, Task
import random


class EventManager:

    def __init__(self, num_tasks: int, lock = None):
        self.event = Condition(lock=lock)
        self.num_tasks = num_tasks
        self.counter = 0
        self.state = 0
        self.tasks: list[Task] = []

    async def sleep(self, secs):
        while secs > self.state:
          await self.wait()

    async def acquire(self):
        await self.event.acquire()

    def notify_all(self):
        self.event.notify_all()

    def sigint_handler(self, sig, frame):
        for task in self.tasks:
            print(task.get_name())
            task.cancel() if not task.done() else ...

    async def event_monitor(self):
        while True:
            async with self.event:
                if self.counter == self.num_tasks:
                    self.counter = 0
                    self.state += 1
                    self.event.notify_all()
                    await asyncio.sleep(0)

    async def wait(self):
        self.counter += 1
        await self.event.wait()

    def release(self):
        self.event.release()

async def long_task1(event: EventManager):
    counter = 0
    while True:
        await event.acquire()
        try:
            await event.wait()
            sleep = random.randint(1, 2)
            await asyncio.sleep(sleep)
            counter += 1
            print(f'task 1: {event.state}-{counter}')
        finally:
            event.release()

async def long_task2(event: EventManager):
    counter = 0
    while True:
        await event.acquire()
        try:
            await event.wait()
            sleep = random.randint(1, 2)
            await asyncio.sleep(sleep)
            counter += 1
            print(f'task 2: {event.state}-{counter}')
        finally:
            event.release()

async def long_task3(event: EventManager):
    sleep = 10
    while True:
        await event.acquire()
        try:
            await event.wait()
            await event.sleep(sleep)
            print(f'task 3: {event.state}-{sleep}')
            sleep += 10
        finally:
            event.release()

async def main():
    manager = EventManager(num_tasks=3)
    signal.signal(signal.SIGINT, manager.sigint_handler)
    task1 = asyncio.create_task(long_task1(manager), name='task1')
    task2 = asyncio.create_task(long_task2(manager), name='task2')
    task3 = asyncio.create_task(long_task3(manager), name='task3')
    control = asyncio.create_task(manager.event_monitor(), name='monitor')
    manager.tasks.extend([task1, task2, task3, control])
    res = await asyncio.gather(task1, task2, task3, control)

asyncio.run(main())
