from concurrent.futures import ThreadPoolExecutor
import asyncio
import random
import time

se = set()
def fun(arg):
    while True:
        time.sleep(10)
        print('sleep')
    # print('sleeping')
    # await asyncio.sleep(random.randint(1, 10))
    # print('wake up')


def nuf():
    while True:
        # time.sleep(5)
        print('awake')


def main(f):
    asyncio.run(f())


async def run():
    # loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=10) as exe:
        exe.submit(fun, 10)
        exe.submit(nuf)
    # r.cancel()
    # print(r.done())
    # return r.result()



asyncio.run(run())

# ars = (1, 3, 4)
#
# def check(f, args):
#     print(*args)
#
#
# b = {check: (3, ars)}

# [k(v[0], v[1]) for k,v in b.items()]