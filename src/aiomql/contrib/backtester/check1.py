class Form:
    rest: str

    @property
    def rest(self):
        return 'rest'


g = Form()
print(g.rest)
