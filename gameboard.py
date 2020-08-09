import pygame

import ui

class Board():
    def __init__(self, dims, coords, colors):
        self.background = pygame.Surface(dims)
        self.background.fill(colors['bg_back'])
        self.coords = coords

        self.menu_bg = ui.Display(dims=(348, 60), coords=(-2, -2), colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 0), offset=(10, 10))
        self.menu_new = ui.Interactive(dims=(52, 40), coords=coords, text='NEW', colors=colors, text_color='light_gray')
        coords = offset_from_element(self.menu_new, corner=(1, 0), offset=(10, 0))
        self.menu_open = ui.Interactive(dims=(63, 40), coords=coords, text='OPEN', text_color='light_gray', colors=colors)
        coords = offset_from_element(self.menu_open, corner=(1, 0), offset=(10, 0))
        self.menu_save = ui.Interactive(dims=(63, 40), coords=coords, text='SAVE', enabled=False, colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 1), offset=(0, 10))
        self.bonus_display = ui.Display(dims=(336, 40), coords=coords, colors=colors, text_color='light_gray', label='BONUS WORD', text_align='center', show_progress=True)
        coords = offset_from_element(self.bonus_display, corner=(0, 1), offset=(0, 10))
        self.level_display = ui.Display(dims=(120, 40), coords=coords, colors=colors, label='LEVEL', text_prefix='Lv ', text_color='light_gray', text_align='center')
        coords = offset_from_element(self.level_display, corner=(1, 0), offset=(10, 0))
        self.multiplier_display = ui.Display(dims=(96, 40), coords=coords, colors=colors, label='MULT.', text_prefix='x', text_color='light_gray', text_align='center')
        coords = offset_from_element(self.multiplier_display, corner=(1, 0), offset=(10, 0))
        self.btn_clear_marked = ui.Interactive(dims=(100, 40), coords=coords, text='UNMARK', enabled=False, colors=colors)
        coords = offset_from_element(self.menu_save, corner=(1, 0), offset=(10, 0))
        self.btn_scramble = ui.Interactive(dims=(120, 40), coords=coords, colors=colors, text='SCRAMBLE', text_color='light_gray')
        coords = offset_from_element(self.btn_scramble, corner=(1, 0), offset=(20, 0))
        self.score_display = ui.Display(dims=(310, 40), coords=coords, colors=colors, text='0', text_color='light_gray', label='SCORE', text_align='center')
        coords = offset_from_element(self.score_display, corner=(0, 1), offset=(0, 10))
        self.word_display = ui.Display(dims=(310, 40), coords=coords, colors=colors, text_color='light_gray', label="SELECTED")
        coords = offset_from_element(self.word_display, corner=(0, 1), offset=(0, 10))
        self.longest_display = ui.Display(dims=(310, 34), coords=coords, colors=colors, label='LONGEST WORD', text_color='beige')
        coords = offset_from_element(self.longest_display, corner=(0, 1), offset=(0, 4))
        self.best_display = ui.Display(dims=(310, 34), coords=coords, colors=colors, label='HIGHEST SCORE', text_color='beige', text_align='left', text_offset=(30, 2))
        coords = offset_from_element(self.best_display, corner=(0, 1), offset=(0, 4))
        self.history_display = ui.Display(dims=(310, 369), coords=coords, colors=colors, label='WORD LIST')

        self.ui_elements = [self.bonus_display, self.score_display, self.word_display, self.history_display, self.longest_display, self.best_display, self.bonus_display, self.level_display, self.multiplier_display, self.btn_clear_marked, self.menu_bg, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]

    def create_tiles(self, colors):
        tiles = []
        # Every other column has 7 and 8 tiles, starting and ending with 7s
        for col in range(7):
            for row in range(7 + col % 2):
                tiles.append(ui.Tile(col=col, row=row, colors=colors))

        return tiles

    def highlight_tiles_from_letter(self, key):
        letter = pygame.key.name(key).upper()
        if letter == 'Q':
            letter = 'Qu'

        # Type currently highlighted key to unhighlight all tiles
        if letter in (last_typed, 'ESCAPE'):
            for t in tiles:
                t.mouse_out()
            return ''
        else:
            # Otherwise, highlight all tiles with matching letters
            for t in tiles:
                if t.letter == letter:
                    t.mouse_over()
                else:
                    t.mouse_out()
        # Return typed key to store as last_typed
        return letter

    def is_neighbor(new_tile, old_tile):

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

    def lookup_letter_value(self, letter):
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

    def update(self):
        if self.tiles:
            self.last = self.tiles[-1]
            self.letters = ''.join([t.letter for t in self.tiles])
            self.length = len(self.letters)
        else:
            self.last = None
            self.letters = None
            self.length = 0

    def update_bonus_color(self, bonus_word, snake_word, colors):
        if bonus_word == snake_word:
            self.bonus_display.set_border_color(colors['green'])
        else:
            self.bonus_display.set_border_color(colors['dark_gray'])

def offset_from_element(element, corner, offset):
    point = [element.coords[i] + element.surf.get_size()[i] if corner[i] else element.coords[i] for i in range(len(corner))]
    return tuple([point[i] + offset[i] for i in range(len(point))])
