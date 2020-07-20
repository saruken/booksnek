import pygame, pygame_gui
import random

import ui_btn

class Board():

    def __init__(self, manager, dictionary):

        self.offset = (10, 10)
        self.dims = (360, 448)
        self.manager = manager

        self.create_bonus_display()

        self.create_tiles()

        self.bonus_counter = 3
        self.set_bonus(dictionary)

    def animate(self):

        to_animate = [t for t in self.tiles if t.target != t.coords]
        if not to_animate:
            return

        for t in to_animate:
            t.ay += .4
            t.coords = (t.coords[0], min(t.coords[1] + t.ay, t.target[1]))
            t.btn.set_position((t.coords[0], t.coords[1]))
            if t.coords[1] == t.target[1]:
                t.ay = 0

    def create_bonus_display(self):

        dims = (356, 40)
        offset = (0, 0)

        self.bonus_display = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(offset, dims), text='BONUS WORD:', manager=self.manager, object_id='#bonus_word')

    def create_tiles(self):

        tiles = []

        # Every other column has 7 and 8 tiles, starting and ending with 7s
        for col in range(7):
            for row in range(7 + col % 2):
                tiles.append(ui_btn.UI_Btn(self.manager, btn_type='tile', col=col, row=row))

        self.tiles = tiles

    def highlight_tiles_from_letter(self, tiles, key, last_typed):

        letter = pygame.key.name(key).upper()
        if letter == 'Q':
            letter = 'Qu'

        # Type currently highlighted key to unhighlight all tiles
        if letter in (last_typed, 'ESCAPE'):
            for t in tiles:
                t.beacon.hide()
            return ''
        else:
            # Otherwise, highlight all tiles with matching letters
            for t in tiles:
                if t.letter == letter:
                    t.beacon.show()
                else:
                    t.beacon.hide()
        # Return typed key to store as last_typed
        return letter

    def lookup_point_value(self, letter):

        if letter in 'AEILNORSTU':
            return 1
        elif letter in 'DG':
            return 2
        elif letter in 'BCMP':
            return 3
        elif letter in 'FHVWY':
            return 4
        elif letter == 'K':
            return 5
        elif letter in 'JX':
            return 8
        else:
            return 10

    def reset_rows(self):

        for col in range(7):
            col_tiles = [t for t in self.tiles if t.col == col]
            # Check if col needs rearranging
            if [x for x in col_tiles if x.row < 0]:
                col_tiles.sort(key=lambda t: t.row)
                for i in range(8):
                    try:
                        # Set row values back to 0-7
                        col_tiles[i].row = i
                        col_tiles[i].set_target(from_row_col=True)
                    except IndexError:
                        # Handle even (7 member) cols
                        pass

    def scramble(self):

        for tile in self.tiles:
            tile.choose_letter()
            tile.update_point_value()
            tile.tile_type = 0
            tile.update_multiplier()
            tile.build_image()
            tile.build_UI()

    def set_bonus(self, dictionary):

        word_pool = [w for w in dictionary if len(w) == self.bonus_counter]
        self.bonus = random.choice(word_pool).upper()

        self.bonus_value = 0
        for letter in self.bonus:
            self.bonus_value += self.lookup_point_value(letter)
        self.bonus_value *= self.bonus_counter
        self.bonus_value += self.bonus_counter * 50

        self.bonus_display.set_text(f'BONUS WORD: {self.bonus} (+{self.bonus_value})')
