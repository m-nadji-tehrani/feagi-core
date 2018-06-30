

class Hope:
    def __init__(self):
        self.param = 10


def test(n):
    for _ in range(n):
        hope = Hope()
        print(n, hope.param)
        hope.param -= 1
        print(">", hope.param)

test(4)
