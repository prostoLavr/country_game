

class Plant:
    def __init__(self, coord, n = 0):
        self.n = 0
        self.coord = coord
        self.is_ill_flag = False

    def grow(self, n=1):
        self.n += 10

    def delete(self):
        pass


class Thing:
    pass


class Scissors(Thing):
    def __init__(self):
        pass

    def cut(self, something):
        something.is_ill_flag = False
        something.n -= 50


class Grass(Plant):
    pass