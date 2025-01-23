import asyncio


async def rt():
    await asyncio.sleep(1)
    print("Hello")

async def rrt():
    while True:
        await asyncio.sleep(15)
        print("rtt")


async def stop(task, tm=10):
    await asyncio.sleep(tm)
    print("Stopping", task)
    res = task.cancel()
    print(res, task)

def main():
    task1 = rt()
    task2 = rrt()
    # task3 = stop(task2)
    tasks = [task1, task2, task3]
    # task = asyncio.gather(*tasks, return_exceptions=True)
    asyncio.run(asyncio.gather(*tasks, return_exceptions=True))
    # await asyncio.gather(task, stop(task, tm=3), return_exceptions=True)

main = main()
# asyncio.run(main)

# def main(a, b=6, **kwargs):
    # print(a, b, kwargs)


# main(4, c=9, g=4, b=99)
