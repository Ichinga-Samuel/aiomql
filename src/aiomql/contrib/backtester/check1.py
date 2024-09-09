from functools import wraps
from dataclasses import dataclass, fields, field
from typing import ClassVar

def dd(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return wrapper

class C:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.tasks = []
            # cls.__init__(a)
            [setattr(cls._instance, k, v) for k, v in kwargs.items()]
        return cls._instance

    def __init__(self, *args, **kwargs):
        print('receiving args')




@dataclass
class D:
    b: int = 0
    c: str = ''
    _fields: list[ClassVar[str]] = field(default_factory=list)

    @dd
    def setattrs(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items() if k in self.fields]

    @property
    def fields(self):
        return self._fields or [name for f in fields(self) if (name := f.name) != '_fields']

d = D()
d.setattrs(r=3)
