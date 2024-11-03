import asyncio

import pytest

from aiomql.lib.bot import Bot


class TestBotFactoryAndExecutor:
    @classmethod
    def setup_class(cls):
        cls.bot = Bot()

    @pytest.fixture(scope="class", autouse=True)
    async def initialize(self):
        self.bot.add_coroutine(coroutine=self.coro_one)
        self.bot.add_coroutine(coroutine=self.coro_two)
        self.bot.add_function(function=self.fun_one)
        self.bot.add_coroutine(coroutine=self.coro_thread, on_separate_thread=True)
        await self.bot.initialize()

    @staticmethod
    def fun_one():
        print("function one")

    @staticmethod
    async def coro_thread():
        while True:
            print("coroutine thread")
            await asyncio.sleep(1)

    @staticmethod
    async def coro_one():
        while True:
            print("coroutine one")
            await asyncio.sleep(1)

    @staticmethod
    async def coro_two():
        while True:
            print("coroutine two")
            await asyncio.sleep(1)

    def test_add_workers(self):
        assert len(self.bot.executor.coroutines) == 3
        assert len(self.bot.executor.functions) == 1
        # task_queue already added coroutine_thread
        assert len(self.bot.executor.coroutine_threads) == 2

    # def
