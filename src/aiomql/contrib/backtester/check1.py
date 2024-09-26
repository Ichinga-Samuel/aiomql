from turtledemo.penrose import start


class Tre:
    def __init__(self):
        self.start = 0
        self.end = 3
        self.span = iter(range(self.start, self.end))

    def __next__(self):
        try:
            next(self.span)
        except StopIteration:
            print('End of range')


r = Tre()
next(r)
next(r)
next(r)
next(r)
