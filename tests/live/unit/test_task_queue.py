import asyncio

from aiomql.core.task_queue import TaskQueue, QueueItem


class TestTaskQueue:
    @classmethod
    def setup_class(cls):
        cls.task_queue = TaskQueue(timeout=5, worker_timeout=1)
        cls.data  = {}

    async def task_one(self):
        for i in range(10):
            await asyncio.sleep(0.5)
            self.data.setdefault('task_one', {})[i] = f"task_one_{i}"

    async def task_two(self):
        for i in range(10):
            await asyncio.sleep(0.5)
            self.data.setdefault('task_two', {})[i] = f"task_two_{i}"

    async def task_three(self):
        for i in range(10):
            self.data.setdefault('task_three', {})[i] = f"task_three_{i}"
            await asyncio.sleep(10)

    async def test_queue(self):
        item_one = QueueItem(self.task_one)
        self.task_queue.add(item=item_one, must_complete=False)
        assert len(self.task_queue.priority_tasks) == 0
        assert self.task_queue.queue.qsize() == 1
        self.task_queue.add(item=QueueItem(self.task_two), must_complete=True)
        assert len(self.task_queue.priority_tasks) == 1
        assert self.task_queue.queue.qsize() == 2
        self.task_queue.add(item=QueueItem(self.task_three), must_complete=False)
        await self.task_queue.run()
        assert len(self.data['task_one']) >= 2
        assert len(self.data['task_two']) == 10
        assert len(self.data['task_three']) == 1
        assert len(self.task_queue.priority_tasks) == 0
