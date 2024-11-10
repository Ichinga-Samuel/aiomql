import asyncio


def run():
    for i in range(10):
        print('running')


async def run_async():
    for i in range(10):
        await asyncio.sleep(1)
        print('running async')


async def main():
    await run_async()
    run()


asyncio.run(main())
