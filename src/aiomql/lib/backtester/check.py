from collections import namedtuple
class ITR:

    def __init__(self) -> None:
        self.span = iter(range(0, 10))
        self.start = 0
    
    def __next__(self):
        self.start = next(self.span)
        return self.start
    

Gender = namedtuple('Gender', ['man', 'woman'])
gen = Gender(man='Manny', woman='Babe')
gend = gen._asdict()
genz = Gender(gend)
print(gen, genz)
# b = ITR()
# print(next(b))
# print(next(b))
# print(next(b))