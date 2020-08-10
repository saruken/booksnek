class Snake():
    def __init__(self):
        self.last = None
        self.length = 0
        self.letters = []
        self.tiles = []
        self.word = ''

    def add(self, tile):
        if tile.tile_type != 'stone':
            self.tiles.append(tile)
            self.update()

    def update(self):
        self.letters = [t.letter for t in self.tiles]
        self.word = ''.join(self.letters)
        self.length = len(self.word)

        if self.tiles:
            self.last = self.tiles[-1]
        else:
            self.last = None
