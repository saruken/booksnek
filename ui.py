import pygame
from math import floor
from numpy.random import choice

class BaseObj:
    def __init__(self, dims, coords, fonts, colors):
        self.colors = colors
        self.fonts = fonts

        self.border_color = self.colors['mid_gray']
        self.coords = coords
        self.dims = dims
        self.interactive = False
        self.surf = pygame.Surface(self.dims)

    def get_abs_rect(self):
        return pygame.Rect(self.coords, self.dims)

class Display(BaseObj):
    def __init__(self, dims, coords, fonts, colors, text=None, text_color=None, text_prefix='', center=False, text_offset=[0, 0], label=None, show_progress=None, multicolor=False):
        super(Display, self).__init__(dims=dims, coords=coords, fonts=fonts, colors=colors)
        self.bg_color = self.colors['bg_main']
        self.bg_progress = self.colors['bg_progress']
        self.border_color = self.colors['mid_gray']
        self.label = label
        self.letter_height = 19
        self.letter_width = 19
        self.multicolor = multicolor
        self.progress = 0
        self.progress_actual = 0
        self.fade_counter = 0
        self.fade_counter_speed = 1.2
        self.progress_lv_increment = 100
        self.progress_max = self.progress_lv_increment
        self.show_progress = show_progress
        self.progress_bar_max_width = None
        self.text = text
        self.center = center
        self.text_color = self.colors[text_color] if text_color else None
        self.text_obj = None
        self.text_offset = text_offset
        self.text_prefix = text_prefix

        self.build_image()

    def build_image(self):
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        if self.show_progress:
            if not self.progress_bar_max_width:
                self.progress_bar_max_width = self.dims[0] - 4
            pygame.draw.rect(self.surf, self.colors['bg_progress'], pygame.Rect((2, self.dims[1] - 6), (self.progress_bar_max_width, 4)))
            bar_width = floor((self.progress / self.progress_max) * self.progress_bar_max_width)
            pygame.draw.rect(self.surf, self.colors['progress'], pygame.Rect((2, self.dims[1] - 6), (bar_width, 4)))
            formatted = format_num(self.progress)
            surf = self.fonts['small'].render(formatted, True, self.colors['mid_gray'], self.bg_color)
            self.surf.blit(surf, dest=(3, self.dims[1] - surf.get_size()[1] - 8))
            formatted = format_num(self.progress_max)
            surf = self.fonts['small'].render(formatted, True, self.colors['mid_gray'], self.bg_color)
            self.surf.blit(surf, dest=(self.dims[0] - surf.get_size()[0] - 3, self.dims[1] - surf.get_size()[1] - 8))

        if self.text:
            # Render text
            surf = self.fonts['medium'].render(str(self.text), True, self.text_color, self.bg_color)
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

    def fade_bg(self):
        try:
            self.bg_color = self.colors['bg_heal'].lerp(self.colors['bg_main'], self.fade_counter / 100.0)
            self.fade_counter += self.fade_counter_speed
        except ValueError:
            self.fade_counter = 0

    def flash(self):
        self.fade_counter = 1

    def set_colored_text(self, text_obj=None):
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        letter_height = 0
        letter_width = 0
        offset_x = 0
        offset_y = 0
        if text_obj:
            self.text_obj = text_obj
        if self.text_obj:
            if type(self.text_obj) is list:
                for entry in text_obj:
                    for index, letter in enumerate(entry['word']):
                        color = entry['colors'][index]
                        surf = self.fonts['medium'].render(letter, True, self.colors[entry['colors'][index]], self.bg_color)
                        if not letter_width:
                            letter_width = surf.get_size()[0]
                        if not letter_height:
                            letter_height = surf.get_size()[1]
                        offset_x = floor((self.dims[0] - letter_width * (len(entry['word']) + len(str(entry["value"])) + 3)) / 2) + letter_width * index
                        if not offset_y:
                            offset_y = floor((self.dims[1] - letter_height) / 2)
                        self.surf.blit(surf, dest=(offset_x, offset_y))

                        surf = self.fonts['medium'].render(f' (+{entry["value"]})', True, self.colors['beige'], self.bg_color)
                        offset_x += letter_width
                        self.surf.blit(surf, dest=(offset_x, offset_y))
            else:
                for index, letter in enumerate(self.text_obj['word']):
                    color = self.text_obj['colors'][index]
                    surf = self.fonts['medium'].render(letter, True, self.colors[self.text_obj['colors'][index]], self.bg_color)
                    if not letter_width:
                        letter_width = surf.get_size()[0]
                    if not letter_height:
                        letter_height = surf.get_size()[1]
                    offset_x = floor((self.dims[0] - letter_width * (len(self.text_obj['word']))) / 2) + letter_width * index
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
        max_lines = floor((self.surf.get_size()[1] - text_offset[1]) / self.letter_height)
        if len(history) > max_lines:
            history = history[-max_lines:]

        container = pygame.Surface(self.dims)
        container.fill(self.bg_color)

        for index_hist, d in enumerate(history):
            for index_letter, letter in enumerate(d['word']):
                surf = self.fonts['medium'].render(letter, True, self.colors[d['colors'][index_letter]], self.bg_color)
                if self.letter_width == 19:
                    self.letter_width = surf.get_size()[0]
                if self.letter_height == 19:
                    self.letter_height = surf.get_size()[1]
                offset = (text_offset[0] + self.letter_width * index_letter, text_offset[1] + self.letter_height * index_hist)
                container.blit(surf, dest=offset)

                if index_letter == len(d['word']) - 1:
                    surf = self.fonts['medium'].render(f' (+{d["value"]})', True, self.colors['beige'], self.bg_color)
                    offset = (text_offset[0] + self.letter_width * (index_letter + 1), text_offset[1] + self.letter_height * index_hist)
                    container.blit(surf, dest=offset)

        self.surf.blit(container, (0, 0))
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((0, 0), (self.dims[0], self.dims[1])), width=15)
        pygame.draw.rect(self.surf, self.border_color, pygame.Rect((0, 0), (self.dims[0], self.dims[1])), width=3)

        if self.label:
            self.set_label()

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
        if self.fade_counter:
            self.fade_bg()
        if self.multicolor:
            self.set_colored_text()
        else:
            self.build_image()

class HPDisplay():
    def __init__(self, dims, coords, fonts, colors):
        self.dims = dims
        self.colors = colors
        self.coords = coords
        self.fade_color = self.colors['red']
        self.fade_counter = 0
        self.fade_counter_speed = 1.2
        self.fonts = fonts
        self.hp = 1
        self.hp_color = self.colors['hp_green']
        self.hp_displayed = 1
        self.hp_max = 1
        self.interactive = False
        self.surf = pygame.Surface(self.dims)

        self.bar_max_width = self.dims[0] - 4
        self.bg_color = self.colors['bg_main']
        self.bg_color_progress = self.colors['bg_progress']
        self.border_color = self.colors['mid_gray']

        self.level_up(lv=1)
        self.build_image()

    def build_image(self):
        self.surf.fill(self.border_color)
        if self.fade_counter:
            try:
                self.bg_color = self.fade_color.lerp(self.colors['bg_main'], self.fade_counter / 100.0)
                self.fade_counter += self.fade_counter_speed
                self.bg_color_progress = self.fade_color.lerp(self.colors['bg_progress'], self.fade_counter / 100.0)
            except ValueError:
                self.fade_counter = 0
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        bar_width = floor((self.hp_displayed / self.hp_max) * self.bar_max_width)
        pygame.draw.rect(self.surf, self.bg_color_progress, pygame.Rect((2, 10), (self.bar_max_width, self.dims[1] - 18)))
        pygame.draw.rect(self.surf, self.hp_color, pygame.Rect((2, 10), (bar_width, self.dims[1] - 18)))
        hp_display = str(round(self.hp_displayed))
        surf = self.fonts['medium'].render(f'{hp_display} / {str(self.hp_max)}', True, self.colors['light_gray'])
        self.surf.blit(surf, dest=(floor((self.dims[0] - surf.get_size()[0]) / 2), floor((self.dims[1] - surf.get_size()[1]) / 2)))
        label = self.fonts['small'].render('HP', True, self.colors['mid_gray'])
        pygame.draw.line(self.surf, self.bg_color, (14, 0), (label.get_size()[0] + 14 + 20, 0), width=2)
        self.surf.blit(label, (24, -2))

    def flash(self, color=None):
        if not self.fade_counter:
            self.fade_counter = 1
        if color:
            self.fade_color = self.colors[color]
        else:
            self.fade_color = self.colors['red']

    def level_up(self, lv):
        base = 108
        new_hp_max = floor((2 * base * lv) / 100) + lv + 10
        delta = new_hp_max - self.hp_max
        self.hp_max = new_hp_max
        self.hp += delta

    def set_hp_color(self):
        ratio = self.hp_displayed / self.hp_max
        if ratio <= .25:
            self.hp_color = self.colors['hp_red']
        elif ratio <= .4:
            self.hp_color = self.colors['hp_yellow']
        else:
            self.hp_color = self.colors['hp_green']

    def update(self):
        self.set_hp_color()
        self.build_image()

class Interactive(BaseObj):
    def __init__(self, name, dims, coords, fonts, colors, text, text_color=None, enabled=True):
        super(Interactive, self).__init__(dims=dims, coords=coords, fonts=fonts, colors=colors)
        self.bg_color = self.colors['ocean']
        self.border_color = None
        self.enabled = enabled
        self.hovered = False
        self.interactive = True
        self.name = name
        self.selected = False
        self.text = text

        self.build_image()

    def build_image(self):
        self.set_colors()
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        # Render text
        surf = self.fonts['medium'].render(self.text, True, self.text_color, self.bg_color)
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
            self.text_color = self.colors['poison']

    def update(self):
        self.set_colors()
        self.build_image()

class Tile():
    def __init__(self, fonts,  colors, col, row, offset):
        self.ay = 0
        self.attack_timer = 5
        self.col = col
        self.colors = colors
        self.dims = (48, 48)
        self.first_turn = True
        self.fonts = fonts
        self.hovered = False
        self.interactive = True
        self.level = 1
        self.marked = False
        self.multiplier = 1
        self.offset = offset if self.col % 2 else (offset[0], offset[1] + (self.dims[0] / 2))
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

    def attack_tick(self):
        self.attack_timer -= 1
        if self.attack_timer == 0:
            self.tile_type = 'stone'
            self.letter = '__'
            self.marked = False
            return True
        return False

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
            surf_pts = self.fonts['small'].render(str(format_num(self.point_value)), True, self.text_color, bg_color)
            # Align bottom/right
            pts_offset = tuple([self.surf.get_size()[i] - surf_pts.get_size()[i] - 3 for i in range(2)])
            self.surf.blit(surf_pts, dest=pts_offset)
            # Render letter
            surf = self.fonts['large'].render(self.letter, True, self.text_color, bg_color)
            # Horiz/vert align center
            offset = [floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)]
            # Bump (-1px, -4px); convert offset
            offset = tuple([offset[0], offset[1] - 4])
            # Countdown timer
            if self.tile_type == 'attack':
                surf_timer = self.fonts['small'].render(str(self.attack_timer), True, self.colors['black'], bg_color)
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

    def mouse_over(self):
        self.hovered = True
        self.border_color = self.colors['gold']

    def select(self):
        self.selected = True

    def set_coords(self, dy=0):
        x = self.offset[0] + (self.dims[0] * self.col)
        y = self.offset[1] + (self.dims[1] * self.row) + dy

        self.coords = (x, y)

    def unselect(self):
        self.selected = False

    def reset(self):
        self.attack_timer = 5
        self.first_turn = True
        self.marked = False
        self.selected = False
        self.tile_type = 'normal'

        self.choose_letter()
        self.update_point_value()
        self.set_text_color()

    def set_target(self, from_row_col=False):
        if from_row_col:
            x = self.offset[0] + (self.dims[0] * self.col)
            y = self.offset[1] + (self.dims[1] * self.row)
        else:
            x, y = self.coords

        self.target = (x, y)

    def set_text_color(self):
        if self.tile_type in ('attack', 'poison'):
            self.text_color = self.colors['light_gray']
        else:
            self.text_color = self.colors['black']

    def toggle_mark(self):
        self.marked = not self.marked

    def update(self, level, multiplier):
        self.level = level
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
        if self.tile_type in ('attack', 'poison', 'silver'):
            type_multiplier = 2
        elif self.tile_type in ('gold', 'heal'):
            type_multiplier = 3

        self.point_value = value * self.level * self.multiplier * type_multiplier

def format_num(num):
    if num < 1000:
        return str(num)
    num = float('{:.3g}'.format(floor(num / 10) * 10))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M'][magnitude])
