import pygame
import random

class Snake():

    def __init__(self):

        self.tiles = []
        self.letters = []

    def add(self, tile):

        self.tiles.append(tile)
        self.update_letters()

    def new(self, tile=None):

        self.tiles = [tile] if tile else []
        self.update_letters()

    def rebuild(self, value):

        tile_type = 'normal'
        special_index = 0

        # Crystal tile created when previous word is worth 100+ points
        if value > 100:
            tile_type = 'crystal'
        else:
            # Gold tile created when previous word has 5+ letters
            # (and crystal tile not already being created)
            if len(self.tiles) > 4:
                tile_type = 'gold'

        if tile_type != 'normal':
            # Randomly choose which new tile will have special tile_type
            special_index = random.choice(range(len(self.tiles)))

        for i, tile in enumerate(self.tiles):
            tile.tile_type = tile_type if i == special_index else 'normal'
            tile.update_multiplier()
            tile.update_point_value()
            tile.build_image()
            tile.build_UI()

    def reroll(self):

        for tile in self.tiles:
            tile.choose_letter()
            tile.row = self.set_row(tile)
            # Push tiles with negative rows up off the top of the screen
            tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])

    def set_row(self, tile):
        '''
        Bumps tile rows "up" to a negative index while retaining their
        col values. If there is more than 1 tile to be moved up in a
        given column, we stack these tiles: row = -1, row = -2, etc.

        This fn only returns a row value; it has no bearing on actually
        drawing the tiles.
        '''

        index = self.tiles.index(tile)
        least_row = 0

        if index:
            prev_rows = [t.row for t in self.tiles[:index] if t.col == tile.col]
            if prev_rows:
                least_row = min(prev_rows)

        return least_row - 1

    def trim_to(self, tile):

        # Clicking on the most recently selected tile submits the word;
        # otherwise, clicking on any selected tile deselects all tiles
        # selected after it, but the clicked tile remains selected.
        index = len(self.tiles)

        for t in reversed(self.tiles):
            if t == tile:
                break
            index -= 1

        self.tiles = self.tiles[:index]
        self.update_letters()

    def update_letters(self):

        self.letters = [t.letter.upper() for t in self.tiles] if self.tiles else []
