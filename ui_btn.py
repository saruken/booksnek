import pygame, pygame_gui
from math import floor
from numpy.random import choice

class UI_Btn():

    def __init__(self, manager, btn_type, dims=None, coords=None, col=None, row=None, text_color=None):

        self.btn_type = btn_type
        self.colors = {
            'beige': pygame.Color('#aaaa66'),
            'black': pygame.Color('#000000'),
            'border_active': pygame.Color('#0000ff'),
            'border_dark': pygame.Color('#202d36'),
            'bg_bomb': pygame.Color('#21282d'),
            'bg_normal': pygame.Color('#c1a663'),
            'bg_normal_selected': pygame.Color('#f0d081'),
            'bg_gold': pygame.Color('#ebc334'),
            'bg_gold_selected': pygame.Color('#fcde72'),
            'bg_crystal': pygame.Color('#349eeb'),
            'bg_crystal_selected': pygame.Color('#76bff5'),
            'dark_gray': pygame.Color('#546c7a'),
            'gold': pygame.Color('#fce803'),
            'gray': pygame.Color('#bfb9a8'),
            'green': pygame.Color('#65a669'),
            'ocean': pygame.Color('#244254'),
            'red': pygame.Color('#e05a41'),
            'teal': pygame.Color('#50aef2')
        }
        self.fonts = {
            'btn': pygame.font.Font('VCR_OSD_MONO.ttf', 18),
            'letter': pygame.font.Font('VCR_OSD_MONO.ttf', 36),
            'point_value': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }

        if self.btn_type == 'tile':
            self.ay = 0
            self.col = col
            self.dims = (48, 48)
            self.offset = (10, 50) if self.col % 2 else (10, 50 + (self.dims[0] / 2))
            self.row = row
            self.selected = False
            self.tile_types = ['normal', 'bomb', 'stone', 'gold', 'crystal']
            self.tile_type = 'normal'
        else:
            self.coords = coords
            self.dims = dims

        self.hovered = False
        self.manager = manager
        self.surf = pygame.Surface(self.dims)
        self.text_color = text_color if text_color else self.colors['black']

        if self.btn_type == 'tile':
            self.set_coords()
            self.set_target()
            self.update_multiplier()
            self.choose_letter()
            self.update_point_value()

        self.build_image()
        self.build_UI()

    def build_image(self, border_color=None):

        if self.btn_type == 'tile':
            bg_color = self.colors[f'bg_{self.tile_type}{"_selected" if self.selected else ""}']
        else:
            bg_color = self.colors['ocean']

        if not border_color:
            border_color = self.colors['gray']

        self.surf.fill(border_color)
        pygame.draw.rect(self.surf, bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        if self.btn_type == 'tile':
            # Font.render params: text, antialias, text color, background color
            surf_pts = self.fonts['point_value'].render(str(self.point_value), True, self.colors['black'], bg_color)
            # Align bottom/right
            pts_offset = tuple([self.surf.get_size()[i] - surf_pts.get_size()[i] - 3 for i in range(2)])
            self.surf.blit(surf_pts, dest=pts_offset)

            surf = self.fonts['letter'].render(self.letter, True, self.colors['black'], bg_color)
            # Horiz/vert align center
            offset = [floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)]
            # Bump (-1px, -4px); convert offset
            offset = tuple([offset[0], offset[1] - 4])
        else:
            surf = self.fonts['btn'].render('SCRAMBLE', True, self.colors['gray'], bg_color)
            # Horiz/vert align center
            offset = tuple([floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)])

        self.surf.blit(surf, dest=offset)

    def build_UI(self):

        try:
            self.btn.kill()
        except AttributeError:
            pass

        self.btn = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(self.coords, self.surf.get_size()), image_surface=self.surf, manager=self.manager)

    def choose_letter(self):

        letter_weights = {
            'A': 0.09,
            'B': 0.02,
            'C': 0.02,
            'D': 0.04,
            'E': 0.12,
            'F': 0.02,
            'G': 0.03,
            'H': 0.02,
            'I': 0.09,
            'J': 0.01,
            'K': 0.01,
            'L': 0.04,
            'M': 0.03,
            'N': 0.06,
            'O': 0.08,
            'P': 0.02,
            'Qu': 0.01,
            'R': 0.06,
            'S': 0.05,
            'T': 0.06,
            'U': 0.04,
            'V': 0.02,
            'W': 0.02,
            'X': 0.01,
            'Y': 0.02,
            'Z': 0.01,
        }

        self.letter = str(choice([key for key in letter_weights], 1, p=[letter_weights[key] for key in letter_weights])[0])

    def mouse_out(self):

        self.hovered = False
        self.build_image()
        self.build_UI()

    def mouse_over(self):

        self.hovered = True
        self.build_image(border_color=self.colors['border_active'])
        self.build_UI()

    def select(self):

        self.selected = True
        self.build_image(border_color=self.colors['gray'])
        self.build_UI()

    def set_coords(self, dy=0):

        x = self.offset[0] + (self.dims[0] * self.col)
        y = self.offset[1] + (self.dims[1] * self.row) + dy

        self.coords = (x, y)

    def set_target(self, from_row_col=False):

        if from_row_col:
            x = self.offset[0] + (self.dims[0] * self.col)
            y = self.offset[1] + (self.dims[1] * self.row)
        else:
            x, y = self.coords

        self.target = (x, y)

    def unselect(self):

        self.selected = False
        self.build_image(border_color=self.colors['gray'])
        self.build_UI()

    def update_multiplier(self):

        self.multiplier = 1
        if self.tile_type == 'gold':
            self.multiplier = 3
        elif self.tile_type == 'crystal':
            self.multiplier = 5

    def update_point_value(self):

        value = 0

        if self.letter in 'AEILNORSTU':
            value = 1
        elif self.letter in 'DG':
            value = 2
        elif self.letter in 'BCMP':
            value = 3
        elif self.letter in 'FHVWY':
            value = 4
        elif self.letter == 'K':
            value = 5
        elif self.letter in 'JX':
            value = 8
        else:
            value = 10

        self.point_value = value * self.multiplier
