import pygame
from math import floor
from numpy.random import choice

class BaseObj:
    def __init__(self, dims, coords, colors):
        self.colors = colors
        self.fonts = {
            'btn': pygame.font.Font('VCR_OSD_MONO.ttf', 18),
            'small': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }

        self.border_color = self.colors['mid_gray']
        self.coords = coords
        self.dims = dims
        self.interactive = False
        self.surf = pygame.Surface(self.dims)

    def get_abs_rect(self):
        return pygame.Rect(self.coords, self.dims)

    def set_text_color(self):
        if self.btn_type == 'tile':
            if self.tile_type == 'bomb':
                self.text_color = self.colors['light_gray']
            else:
                self.text_color = self.colors['black']
        else:
            if self.enabled:
                self.text_color = self.colors['light_gray']
            else:
                self.text_color = self.colors['dark_gray']

class Display(BaseObj):
    def __init__(self, dims, coords, colors, text=None, text_color=None, text_prefix='', center=False, text_offset=[0, 0], label=None, show_progress=None):
        super(Display, self).__init__(dims=dims, coords=coords, colors=colors)
        self.bg_color = self.colors['bg_main']
        self.border_color = self.colors['mid_gray']
        self.label = label
        self.letter_height = 19
        self.letter_width = 19
        self.progress = 0
        self.progress_floor = 0
        self.progress_max = 0
        self.show_progress = show_progress
        self.text = text
        self.center = center
        self.text_color = self.colors[text_color] if text_color else None
        self.text_offset = text_offset
        self.text_prefix = text_prefix

        self.update()

    def build_image(self):
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        if self.show_progress:
            if not self.progress_max:
                self.progress_max = self.dims[0] - 4
            pygame.draw.rect(self.surf, self.colors['bg_progress'], pygame.Rect((2, self.dims[1] - 6), (self.progress_max, 4)))
            pygame.draw.rect(self.surf, self.colors['progress'], pygame.Rect((2, self.dims[1] - 6), (self.progress, 4)))

        if self.text:
            # Render text
            surf = self.fonts['btn'].render(str(self.text), True, self.text_color, self.bg_color)
            # Horiz align
            if self.center:
                offset_x = floor((self.surf.get_size()[0] - surf.get_size()[0]) / 2) + self.text_offset[0]
            else:
                offset_x = self.text_offset[0]
            # Vert align
            offset_y = floor((self.surf.get_size()[1] - surf.get_size()[1]) / 2) + self.text_offset[1]
            self.surf.blit(surf, dest=(offset_x, offset_y))

        if self.label:
            self.set_label()

    def set_colored_text(self, text_obj):
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        letter_height = 0
        letter_width = 0
        offset_x = 0
        offset_y = 0
        if type(text_obj) is list:
            for entry in text_obj:
                for index, letter in enumerate(entry['word']):
                    color = entry['colors'][index]
                    surf = self.fonts['btn'].render(letter, True, self.colors[entry['colors'][index]], self.bg_color)
                    if not letter_width:
                        letter_width = surf.get_size()[0]
                    if not letter_height:
                        letter_height = surf.get_size()[1]
                    offset_x = floor((self.dims[0] - letter_width * (len(entry['word']) + len(str(entry["value"])) + 3)) / 2) + letter_width * index
                    if not offset_y:
                        offset_y = floor((self.dims[1] - letter_height) / 2)
                    self.surf.blit(surf, dest=(offset_x, offset_y))

                    surf = self.fonts['btn'].render(f' (+{entry["value"]})', True, self.colors['beige'], self.bg_color)
                    offset_x += letter_width
                    self.surf.blit(surf, dest=(offset_x, offset_y))
        else:
            for index, letter in enumerate(text_obj['word']):
                color = text_obj['colors'][index]
                surf = self.fonts['btn'].render(letter, True, self.colors[text_obj['colors'][index]], self.bg_color)
                if not letter_width:
                    letter_width = surf.get_size()[0]
                if not letter_height:
                    letter_height = surf.get_size()[1]
                offset_x = floor((self.dims[0] - letter_width * (len(text_obj['word']))) / 2) + letter_width * index
                if not offset_y:
                    offset_y = floor((self.dims[1] - letter_height) / 2)
                self.surf.blit(surf, dest=(offset_x, offset_y))

        self.text = ''

        if self.label:
            self.set_label()

    def set_label(self):
        text = self.fonts['small'].render(str(self.label), True, self.colors['mid_gray'], self.bg_color)
        surf = pygame.Surface((text.get_size()[0] + 20, text.get_size()[1]))
        surf.fill(self.bg_color)
        surf.blit(text, (10, 0))
        self.surf.blit(surf, (14, -2))

    def set_multiline_text(self, history):

        '''
        Items in the 'history' list are dicts. They have the following keys:
            word   - Word (str)
            value  - Point value (int)
            colors - Letter colors (list of strings):
        '''
        text = ''
        text_offset = (8, 10)

        self.surf.fill(self.bg_color)

        max_lines = floor((self.surf.get_size()[1] - text_offset[1]) / self.letter_height)
        if len(history) > max_lines:
            history = history[-max_lines:]

        container = pygame.Surface((self.dims[0], self.dims[1]))

        container.fill(self.bg_color)

        for index_hist, d in enumerate(history):
            for index_letter, letter in enumerate(d['word']):
                surf = self.fonts['btn'].render(letter, True, self.colors[d['colors'][index_letter]], self.bg_color)
                if self.letter_width == 19:
                    self.letter_width = surf.get_size()[0]
                if self.letter_height == 19:
                    self.letter_height = surf.get_size()[1]
                offset = (text_offset[0] + self.letter_width * index_letter, text_offset[1] + self.letter_height * index_hist)
                container.blit(surf, dest=offset)

                if index_letter == len(d['word']) - 1:
                    surf = self.fonts['btn'].render(f' (+{d["value"]})', True, self.colors['beige'], self.bg_color)
                    offset = (text_offset[0] + self.letter_width * (index_letter + 1), text_offset[1] + self.letter_height * index_hist)
                    container.blit(surf, dest=offset)

        self.surf.blit(container, (0, 0))
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((0, 0), (self.dims[0], self.dims[1])), width=15)
        pygame.draw.rect(self.surf, self.border_color, pygame.Rect((0, 0), (self.dims[0], self.dims[1])), width=3)

        if self.label:
            self.set_label()

    def set_progress(self, score, mult):
        self.progress = floor((score - self.progress_floor) / (1000 * mult) * self.progress_max)

    def set_text(self, text):
        if text:
            self.update(text=text)
        else:
            self.update(text='__clear__')

    def update(self, text=None):
        if text:
            if text == '__clear__':
                self.text = None
            else:
                self.text = self.text_prefix + str(text)
        self.build_image()

class Interactive(BaseObj):
    def __init__(self, dims, coords, colors, text, text_color=None, enabled=True):
        super(Interactive, self).__init__(dims=dims, coords=coords, colors=colors)
        self.bg_color = self.colors['ocean']
        self.border_color = None
        self.enabled = enabled
        self.hovered = False
        self.interactive = True
        self.selected = False
        self.text = text

        self.build_image()

    def build_image(self):
        self.set_colors()
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        # Render text
        surf = self.fonts['btn'].render(self.text, True, self.text_color, self.bg_color)
        # Horiz/vert align center
        offset = tuple([floor((self.dims[i]) - surf.get_size()[i]) / 2 for i in range(2)])

        self.surf.blit(surf, dest=offset)

    def mouse_out(self):
        self.hovered = False
        self.update()

    def mouse_over(self):
        self.hovered = True
        self.update()

    def set_colors(self):
        if self.enabled:
            self.text_color = self.colors['light_gray']
            if self.hovered:
                self.border_color = self.colors['light_gray']
            else:
                self.border_color = self.colors['mid_gray']

        else:
            self.border_color = self.colors['ocean']
            self.text_color = self.colors['bomb']

    def update(self):
        self.set_colors()
        self.build_image()

class Tile():
    def __init__(self, colors, col, row):
        self.ay = 0
        self.bomb_timer = 5
        self.col = col
        self.colors = colors
        self.dims = (48, 48)
        self.fonts = {
            'letter': pygame.font.Font('VCR_OSD_MONO.ttf', 36),
            'small': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }
        self.hovered = False
        self.interactive = True
        self.level = 1
        self.marked = False
        self.multiplier = 1
        self.offset = (10, 168) if self.col % 2 else (10, 168 + (self.dims[0] / 2))
        self.point_value = 0
        self.row = row
        self.selected = False
        self.surf = pygame.Surface(self.dims)
        self.text_color = self.colors['black']
        self.tile_type = 'normal'

        self.bg_color = self.colors['beige']
        self.border_color = self.colors['light_gray']

        self.set_coords()
        self.set_target()
        self.choose_letter()
        self.update_point_value()
        self.set_text_color()

        self.update()

    def bomb_tick(self):
        self.bomb_timer -= 1
        if self.bomb_timer == 0:
            self.tile_type = 'stone'
            self.letter = '__'

    def build_image(self):
        bg_color = self.colors[f'bg_{self.tile_type}{"_selected" if self.selected else ""}']

        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        if self.tile_type == 'stone':
            surf = pygame.Surface((self.dims[0] - 4, self.dims[1] - 4))
            surf.fill(bg_color)
            offset = (2, 2)
        else:
            # Render point value
            surf_pts = self.fonts['small'].render(str(self.point_value), True, self.text_color, bg_color)
            # Align bottom/right
            pts_offset = tuple([self.surf.get_size()[i] - surf_pts.get_size()[i] - 3 for i in range(2)])
            self.surf.blit(surf_pts, dest=pts_offset)
            # Render letter
            surf = self.fonts['letter'].render(self.letter, True, self.text_color, bg_color)
            # Horiz/vert align center
            offset = [floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)]
            # Bump (-1px, -4px); convert offset
            offset = tuple([offset[0], offset[1] - 4])

            if self.tile_type == 'bomb':
                surf_timer = self.fonts['small'].render(str(self.bomb_timer), True, self.colors['red'], bg_color)
                # Align bottom/left
                timer_offset = (3, self.dims[1] - surf_timer.get_size()[1] - 3)
                self.surf.blit(surf_timer, dest=timer_offset)

        self.surf.blit(surf, dest=offset)
        if self.marked:
            pygame.draw.circle(self.surf, self.colors['mid_gray'], (8, 8), 4)
            pygame.draw.circle(self.surf, self.colors['teal'], (8, 8), 2)

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
        self.hovered = False
        self.border_color = self.colors['light_gray']
        self.build_image()

    def mouse_over(self):
        self.hovered = True
        self.border_color = self.colors['gold']
        self.build_image()

    def select(self):
        self.selected = True
        self.build_image()

    def set_coords(self, dy=0):
        x = self.offset[0] + (self.dims[0] * self.col)
        y = self.offset[1] + (self.dims[1] * self.row) + dy

        self.coords = (x, y)

    def unselect(self):
        self.selected = False
        self.build_image()

    def reset(self):
        self.bomb_timer = 5
        self.marked = False
        self.selected = False
        self.tile_type = 'normal'

        self.choose_letter()
        self.update_point_value()
        self.set_text_color()
        self.update()

    def set_target(self, from_row_col=False):
        if from_row_col:
            x = self.offset[0] + (self.dims[0] * self.col)
            y = self.offset[1] + (self.dims[1] * self.row)
        else:
            x, y = self.coords

        self.target = (x, y)

    def set_text_color(self):
        pass

    def toggle_mark(self, board_mult):
        self.marked = not self.marked
        self.update()

    def update(self, level=None, multiplier=None):
        if self.tile_type == 'bomb':
            self.bomb_tick()

        if level:
            self.level = level
        if multiplier:
            self.multiplier = multiplier

        self.update_point_value()
        self.set_text_color()
        self.build_image()

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

        type_multiplier = 1
        if self.tile_type in ('bomb', 'silver'):
            type_multiplier = 2
        elif self.tile_type == 'gold':
            type_multiplier = 3
        elif self.tile_type == 'crystal':
            type_multiplier = 5

        self.point_value = value * self.level * self.multiplier * type_multiplier
