import asyncio
import inspect
from functools import cache, lru_cache, cached_property, wraps, partial

# from

def async_cache(fun):

    @wraps(fun)
    async def wrapper(*args, **kwargs):
        print(wrapper.cache)
        key = (args, frozenset(kwargs.items()))
        async with wrapper.lock:
            if key not in wrapper.cache:
                print('not in cache')
                wrapper.cache[key] = await fun(*args, **kwargs)
        return wrapper.cache[key]

    wrapper.lock = asyncio.Lock()
    wrapper.cache = {}
    return wrapper


class Test:

    def __init__(self):
        self.rr = 0

    def __repr__(self):
        return f'{self.__class__.__name__}(...)'

    @async_cache
    async def check(self, a, b):
        an = a + b - self.rr
        return an

# async def main(a, b):
#     t = Test()
#
#     @async_cache
#     def check(_a, _b):
#         an = _a + _b
#         print('check', _a, _b, t.rr)
#         return an
#
#     return check(a, b)

t = Test()
y = asyncio.run(t.check(1, 2))
t.rr = 6
y1 = asyncio.run(t.check(1, 2))
t.rr = 7
y2 = asyncio.run(t.check(1, 2))
print(y, y1, y2)

@async_cache
async def func(a, b):
    an = a + b
    print('func')
    return an

@async_cache
async def func1(e, c=6, d=6):
    an = e - c + d
    print('func1')
    return an


# asyncio.run(func(1, 2))
# asyncio.run(func1(1, d=8))
# asyncio.run(func(1, 2))
# asyncio.run(func(1, 3))
# asyncio.run(func1(1, d=6))
# asyncio.run(func1(1, d=6))
# asyncio.run(func1(1, d=7))
