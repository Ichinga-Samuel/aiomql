def fun(a, b=6, *c, **d):
    print(f"{a=}, {b=}, {c=}, {d=}")

fun(1, 3, 4, 5, six=6, seven=7)
