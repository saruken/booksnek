import pygame
import random
from math import log10
from numpy.random import choice

class Snake():

    def __init__(self):

        self.tiles = []
        self.letters = []

    def add(self, tile):

        if tile.tile_type != 'stone':
            self.tiles.append(tile)
            self.update_letters()

    def get_bomb_weight(self, avg):

        return max(round((-0.5 * log10(0.34 * avg - 1)), 2), 0)

    def new(self, tile=None):

        if tile:
            if tile.tile_type != 'stone':
                self.tiles = [tile]
        else:
            self.tiles = []
        self.update_letters()

    def rebuild(self, value, last_five, mult):

        tile_type = 'normal'
        special_index = 0

        # Bomb tiles are created when your last 5 words have been on the
        # short side. Generally, maintaining an average of 5 letters
        # keeps you safe; anything below this and there's a better
        # chance of a bomb tile spawning.
        # avg = 5; bomb = 8%
        # avg = 3; bomb = 85%
        if len(last_five) == 5:
            avg = round(sum(last_five) / len(last_five), 1)
            # Keep bomb_weight non-negative
            bomb_weight = self.get_bomb_weight(avg)
            normal_weight = 1 - bomb_weight
            tile_type = choice(['normal', 'bomb'], 1, p=[normal_weight, bomb_weight])[0]

        # Crystal tile created when previous word is worth 100+ points
        # Crystal/gold overrides a bomb, if one would have been created.
        if value > 100:
            tile_type = 'crystal'
        else:
            # Gold tile created when previous word has 5+ letters
            # (and crystal tile not already being created)
            if len(''.join(self.letters)) > 4:
                tile_type = 'gold'

        if tile_type != 'normal':
            # Randomly choose which new tile will have special tile_type
            special_index = random.choice(range(len(self.tiles)))

        for i, tile in enumerate(self.tiles):
            tile.tile_type = tile_type if i == special_index else 'normal'
            tile.bomb_timer = 6
            tile.update(mult)

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
