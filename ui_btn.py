import pygame
from math import floor
from numpy.random import choice

class UI_Btn():

    def __init__(self, btn_type, dims=None, coords=None, col=None, row=None, text=None, text_color=None, border_color=None, enabled=True, can_mark=False):

        self.btn_type = btn_type
        self.colors = {
            'beige': pygame.Color('#aaaa66'),
            'bg_bomb': pygame.Color('#3b3245'),
            'bg_bomb_selected': pygame.Color('#655775'),
            'bg_crystal': pygame.Color('#349eeb'),
            'bg_crystal_selected': pygame.Color('#76bff5'),
            'bg_gold': pygame.Color('#ebc334'),
            'bg_gold_selected': pygame.Color('#fcde72'),
            'bg_gray': pygame.Color('#4e575c'),
            'bg_gray_inactive': pygame.Color('#4e575c'),
            'bg_normal': pygame.Color('#c1a663'),
            'bg_normal_selected': pygame.Color('#f0d081'),
            'bg_silver': pygame.Color('#9eadad'),
            'bg_silver_selected': pygame.Color('#d5e7e8'),
            'bg_stone': pygame.Color('#5f666b'),
            'black': pygame.Color('#000000'),
            'border_active': pygame.Color('#546c7a'),
            'border_dark': pygame.Color('#202d36'),
            'dark_gray': pygame.Color('#546c7a'),
            'bomb': pygame.Color('#7c6e8a'),
            'gold': pygame.Color('#fce803'),
            'gray': pygame.Color('#bfb9a8'),
            'green': pygame.Color('#65a669'),
            'ocean': pygame.Color('#244254'),
            'red': pygame.Color('#e05a41'),
            'silver': pygame.Color('#d5e7e8'),
            'teal': pygame.Color('#50aef2')
        }
        self.fonts = {
            'btn': pygame.font.Font('VCR_OSD_MONO.ttf', 18),
            'letter': pygame.font.Font('VCR_OSD_MONO.ttf', 36),
            'point_value': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }

        if self.btn_type == 'tile':
            self.ay = 0
            self.bomb_timer = 5
            self.col = col
            self.dims = (48, 48)
            self.offset = (10, 168) if self.col % 2 else (10, 168 + (self.dims[0] / 2))
            self.row = row
            self.selected = False
            self.tile_type = 'normal'
        else:
            self.coords = coords
            self.dims = dims

        self.btn = pygame.Surface(self.dims)
        self.can_click = True
        self.can_hover = True
        self.can_mark = can_mark
        self.enabled = enabled
        self.hovered = False
        self.marked = False
        self.surf = pygame.Surface(self.dims)
        self.text = text
        self.text_color = text_color if text_color else self.colors['border_dark']

        if self.btn_type == 'tile':
            self.set_coords()
            self.set_target()
            self.update_multiplier()
            self.choose_letter()
            self.update_point_value()
            self.set_text_color()

        if border_color:
            self.build_image(self.colors[border_color])
        else:
            self.build_image()
        self.build_UI()

    def build_image(self, border_color=None):

        if self.btn_type == 'tile':
            bg_color = self.colors[f'bg_{self.tile_type}{"_selected" if self.selected else ""}']
        else:
            if self.enabled:
                bg_color = self.colors['ocean']
            else:
                bg_color = self.colors['bg_gray_inactive']

        if not border_color:
            if self.enabled:
                border_color = self.colors['gray']
            else:
                border_color = self.colors['ocean']

        self.surf.fill(border_color)
        pygame.draw.rect(self.surf, bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        if self.btn_type == 'tile':
            if self.tile_type == 'stone':
                surf = pygame.Surface((self.dims[0] - 4, self.dims[1] - 4))
                surf.fill(bg_color)
                offset = (2, 2)
            else:
                # Font.render params: text, antialias, text color, background color
                surf_pts = self.fonts['point_value'].render(str(self.point_value), True, self.text_color, bg_color)
                # Align bottom/right
                pts_offset = tuple([self.surf.get_size()[i] - surf_pts.get_size()[i] - 3 for i in range(2)])
                self.surf.blit(surf_pts, dest=pts_offset)

                surf = self.fonts['letter'].render(self.letter, True, self.text_color, bg_color)
                # Horiz/vert align center
                offset = [floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)]
                # Bump (-1px, -4px); convert offset
                offset = tuple([offset[0], offset[1] - 4])

                if self.tile_type == 'bomb':
                    surf_timer = self.fonts['point_value'].render(str(self.bomb_timer), True, self.colors['red'], bg_color)
                    # Align bottom/left
                    timer_offset = (3, self.dims[1] - surf_timer.get_size()[1] - 3)
                    self.surf.blit(surf_timer, dest=timer_offset)

        else:
            surf = self.fonts['btn'].render(self.text, True, self.text_color, bg_color)
            # Horiz/vert align center
            offset = tuple([floor((self.dims[i]) - surf.get_size()[i]) / 2 for i in range(2)])

        self.surf.blit(surf, dest=offset)
        if self.marked:
            pygame.draw.circle(self.surf, self.colors['dark_gray'], (8, 8), 4)
            pygame.draw.circle(self.surf, self.colors['teal'], (8, 8), 2)

    def build_UI(self):

        self.btn.blit(self.surf, (0, 0))

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

    def get_abs_rect(self):

        return pygame.Rect(self.coords, self.dims)

    def mouse_out(self):

        if self.can_hover:
            self.hovered = False
            self.build_image()
            self.build_UI()

    def mouse_over(self):

        if self.can_hover:
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

    def set_text_color(self):

        if self.btn_type == 'tile':
            if self.tile_type == 'bomb':
                self.text_color = self.colors['gray']
            else:
                self.text_color = self.colors['black']
        else:
            if self.enabled:
                self.text_color = self.colors['gray']
            else:
                self.text_color = self.colors['border_dark']

    def toggle_mark(self, board_mult):

        self.marked = not self.marked
        self.update(board_mult)

    def unselect(self):

        self.selected = False
        self.build_image(border_color=self.colors['gray'])
        self.build_UI()

    def update(self, board_mult=1):

        if self.btn_type == 'tile':
            if self.tile_type == 'bomb':
                if self.bomb_timer == 0:
                    self.tile_type = 'stone'
                    self.letter = '_'

            self.update_multiplier()
            self.update_point_value(board_mult)

        self.set_text_color()
        self.build_image()
        self.build_UI()

    def update_multiplier(self):

        self.multiplier = 1
        if self.tile_type in ('bomb', 'silver'):
            self.multiplier = 2
        elif self.tile_type == 'gold':
            self.multiplier = 3
        elif self.tile_type == 'crystal':
            self.multiplier = 5

    def update_point_value(self, mult=1):

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

        self.point_value = value * self.multiplier * mult
