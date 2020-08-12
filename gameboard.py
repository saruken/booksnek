import pygame

import ui

class Board():
    def __init__(self, dims, coords, colors):
        self.background = pygame.Surface(dims)
        self.background.fill(colors['bg_back'])
        self.coords = coords

        self.menu_bg = ui.Display(dims=(348, 60), coords=(-2, -2), colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 0), offset=(10, 10))
        self.menu_new = ui.Interactive(name='new', dims=(52, 40), coords=coords, text='NEW', colors=colors, text_color='light_gray')
        coords = offset_from_element(self.menu_new, corner=(1, 0), offset=(10, 0))
        self.menu_open = ui.Interactive(name='open', dims=(63, 40), coords=coords, text='OPEN', text_color='light_gray', colors=colors)
        coords = offset_from_element(self.menu_open, corner=(1, 0), offset=(10, 0))
        self.menu_save = ui.Interactive(name='save', dims=(63, 40), coords=coords, text='SAVE', enabled=False, colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 1), offset=(12, 10))
        self.bonus_display = ui.Display(dims=(336, 40), coords=coords, colors=colors, text_color='light_gray', label='MULTIPLIER+', center=True)
        coords = offset_from_element(self.bonus_display, corner=(0, 1), offset=(0, 10))
        self.level_display = ui.Display(dims=(136, 40), coords=coords, colors=colors, label='EXP.', text_prefix='Lv ', text_color='light_gray', center=True, show_progress=True)
        coords = offset_from_element(self.level_display, corner=(1, 0), offset=(10, 0))
        self.multiplier_display = ui.Display(dims=(80, 40), coords=coords, colors=colors, label='MULT.', text_prefix='x', text_color='light_gray', center=True)
        coords = offset_from_element(self.multiplier_display, corner=(1, 0), offset=(10, 0))
        self.btn_clear_marked = ui.Interactive(name='clear', dims=(100, 40), coords=coords, text='UNMARK', enabled=False, colors=colors)
        coords = offset_from_element(self.menu_save, corner=(1, 0), offset=(10, 0))
        self.btn_scramble = ui.Interactive(name='scramble', dims=(120, 40), coords=coords, colors=colors, text='SCRAMBLE', text_color='light_gray')
        coords = offset_from_element(self.btn_scramble, corner=(1, 0), offset=(20, 0))
        self.score_display = ui.Display(dims=(310, 40), coords=coords, colors=colors, text='0', text_color='light_gray', label='SCORE', center=True)
        coords = offset_from_element(self.score_display, corner=(0, 1), offset=(0, 10))
        self.word_display = ui.Display(dims=(310, 40), coords=coords, colors=colors, text_color='light_gray', label="SELECTED", center=True)
        coords = offset_from_element(self.word_display, corner=(0, 1), offset=(0, 10))
        self.longest_display = ui.Display(dims=(310, 34), coords=coords, colors=colors, label='LONGEST WORD', text_color='beige', center=True)
        coords = offset_from_element(self.longest_display, corner=(0, 1), offset=(0, 4))
        self.best_display = ui.Display(dims=(310, 34), coords=coords, colors=colors, label='HIGHEST SCORE', text_color='beige', center=True, text_offset=(30, 2))
        coords = offset_from_element(self.best_display, corner=(0, 1), offset=(0, 4))
        self.history_display = ui.Display(dims=(310, 369), coords=coords, colors=colors, label='WORD LIST')

        self.menu_btns = [self.btn_clear_marked, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]
        self.ui_elements = [self.bonus_display, self.score_display, self.word_display, self.history_display, self.longest_display, self.best_display, self.bonus_display, self.level_display, self.multiplier_display, self.btn_clear_marked, self.menu_bg, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]

    def create_tiles(self, colors):
        tiles = []
        # Every other column has 7 and 8 tiles, starting and ending with 7s
        for col in range(7):
            for row in range(7 + col % 2):
                tiles.append(ui.Tile(col=col, row=row, colors=colors))

        return tiles

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

def offset_from_element(element, corner, offset):
    point = [element.coords[i] + element.surf.get_size()[i] if corner[i] else element.coords[i] for i in range(len(corner))]
    return tuple([point[i] + offset[i] for i in range(len(point))])
