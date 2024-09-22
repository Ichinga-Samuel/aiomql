from functools import cached_property
class Data:
    def __init__(self):
        self.a = 1
        self.b = 2

class TData:
    _a: int
    _b: int
    _dat: dict

    def __init__(self):
        self._data = Data()

    def __getattr__(self, item):
        if val := self.__annotations__.get(item):
            return getattr(self._data, item, val())

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, val):
        self._a = val

    @property
    def dat(self):
        return self._dat

    @dat.setter
    def dat(self, key, val):
        self._dat |= val

    @dat.deleter
    def dat(self):
        self._dat = {}


f = TData()
# f.data = {'a': 1}
print(f.a)
