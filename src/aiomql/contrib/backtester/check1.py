glob = dict()

class Check:
    def __init__(self, ty):
        self.r = ty

    @property
    def r(self):
        print('getting value')
        return glob.get('r')

    @r.setter
    def r(self, value):
        print('setting value')
        glob['r'] = value


f = Check(465)
print(f.r)
f.r = 56
print(f.r)
