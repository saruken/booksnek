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

    def is_neighbor(self, new_tile, old_tile=None):

        '''
        There are 4 'false' neighbors, depending on which col old_tile
        is in:
            Even old_tile.cols:
                new_c == old_c + 1 and new_r == old_r + 1
                new_c == old_c - 1 and new_r == old_r + 1
            Odd old_tile.cols:
                new_c == old_c - 1 and new_r == old_r - 1
                new_c == old_c + 1 and new_r == old_r - 1
        These look good on paper, but looking at the actual arrangement
        of tiles shows them to be erroneous:

            E C
            V O           O C
            E L           D O
            N             D L

            B B       A A     C C
        A A B B C C   A A 1 1 C C
        A A 1 1 C C   0 0 1 1 2 2
        0 0 1 1 2 2   0 0 X X 2 2
        0 0 X X 2 2   5 5 X X 3 3
        5 5 X X 3 3   5 5 4 4 3 3
        5 5 4 4 3 3   F F 4 4 D D
        F F 4 4 D D   F F E E D D
        F F E E D D       E E
            E E

        'X' = old_tile
        'D' and 'F' are false neighbors for even column 'X' tiles
        'A' and 'C' are false neighbors for odd column 'X' tiles
        '''

        if not old_tile:
            old_tile = self.last
        new_c, old_c = new_tile.col, old_tile.col
        new_r, old_r = new_tile.row, old_tile.row

        # Odd columns
        if old_tile.col % 2:
            # 2 o'clock
            if new_c == old_c + 1 and new_r == old_r - 1:
                return True
            # 4 o'clock
            elif new_c == old_c + 1 and new_r == old_r:
                return True
            # 8 o'clock
            elif new_c == old_c - 1 and new_r == old_r:
                return True
            # 10 o'clock
            elif new_c == old_c - 1 and new_r == old_r - 1:
                return True

        # Even columns
        else:
            # 2 o'clock
            if new_c == old_c + 1 and new_r == old_r:
                return True
            # 4 o'clock
            elif new_c == old_c + 1 and new_r == old_r + 1:
                return True
            # 8 o'clock
            elif new_c == old_c - 1 and new_r == old_r + 1:
                return True
            # 10 o'clock
            elif new_c == old_c - 1 and new_r == old_r:
                return True

        # Parity agnostic columns
        # 12 o'clock
        if new_c == old_c and new_r == old_r - 1:
            return True
        # 6 o'clock
        elif new_c == old_c and new_r == old_r + 1:
            return True

        # Self
        if old_tile  == new_tile:
            return True

        return False

    def update(self):
        self.letters = [t.letter for t in self.tiles]
        self.word = ''.join(self.letters)
        self.length = len(self.word)

        if self.tiles:
            self.last = self.tiles[-1]
        else:
            self.last = None
