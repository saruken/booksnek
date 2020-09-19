import os, pygame, random
from math import ceil, floor, sqrt

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
    def __init__(self, dims, coords, fonts, colors, text=None, text_color=None, text_prefix='', center=False, vert_center=True, text_offset=[0, 0], label=None, show_progress=None, multicolor=False):
        super(Display, self).__init__(dims=dims, coords=coords, fonts=fonts, colors=colors)
        self.bg_color = self.colors['bg_main']
        self.bg_progress = self.colors['bg_progress']
        self.border_color = self.colors['mid_gray']
        self.hovered = False
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
        self.text_color = self.colors[text_color] if text_color else self.colors['light_gray']
        self.text_obj = None
        self.text_offset = text_offset
        self.text_prefix = text_prefix
        self.vert_center = vert_center

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
            self.surf.blit(surf, dest=(5, self.dims[1] - surf.get_size()[1] - 8))
            formatted = format_num(self.progress_max)
            surf = self.fonts['small'].render(formatted, True, self.colors['mid_gray'], self.bg_color)
            self.surf.blit(surf, dest=(self.dims[0] - surf.get_size()[0] - 5, self.dims[1] - surf.get_size()[1] - 8))

        if self.text:
            # Render text
            surf = self.fonts['medium'].render(str(self.text), True, self.text_color, self.bg_color)
            # Horiz align
            if self.center:
                offset_x = floor((self.surf.get_size()[0] - surf.get_size()[0]) / 2) + self.text_offset[0]
            else:
                offset_x = self.text_offset[0]
            # Vert align
            if self.vert_center:
                offset_y = floor((self.surf.get_size()[1] - surf.get_size()[1]) / 2) + self.text_offset[1]
            else: offset_y = self.text_offset[1]
            self.surf.blit(surf, dest=(offset_x, offset_y))

        if self.label:
            self.set_label()

    def fade_border(self):
        try:
            self.border_color = self.colors['bg_heal'].lerp(self.colors['mid_gray'], self.fade_counter / 100.0)
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
        text_offset = (8, 12)
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

    def update(self, text=None, label=None):
        if text:
            if text == '__clear__':
                self.text = None
            else:
                self.text = self.text_prefix + str(text)
        if label:
            self.label = label
        if self.fade_counter:
            self.fade_border()
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
        self.hp_max = 15
        self.hp_max_base = 15
        self.interactive = False
        self.surf = pygame.Surface(self.dims)

        self.bar_max_width = self.dims[0] - 4
        self.bg_color = self.colors['bg_main']
        self.bg_color_progress = self.colors['bg_progress']
        self.border_color = self.colors['mid_gray']

    def build_image(self):
        if self.fade_counter:
            try:
                self.border_color = self.fade_color.lerp(self.colors['mid_gray'], self.fade_counter / 100.0)
                self.fade_counter += self.fade_counter_speed
            except ValueError:
                if self.hp_displayed == self.hp:
                    self.fade_counter = 0
                else:
                    self.fade_counter = -1
        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        bar_width = floor((self.hp_displayed / self.hp_max) * self.bar_max_width)
        pygame.draw.rect(self.surf, self.bg_color_progress, pygame.Rect((2, 10), (self.bar_max_width, self.dims[1] - 18)))
        pygame.draw.rect(self.surf, self.hp_color, pygame.Rect((2, 10), (bar_width, self.dims[1] - 18)))
        hp_display = str(max(round(self.hp_displayed), 0))
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
        buff = random.choice([1, 2, 3])
        self.hp_max += buff
        self.hp += buff
        self.hp_displayed += buff
        print(f'HP and HP_MAX increased by {buff}: {self.hp} / {self.hp_max}')
        self.update()
        return buff

    def set_hp_color(self):
        lr = self.hp_displayed / self.hp_max
        w = (self.hp_max / 2)
        if lr <= .5:
            color0 = self.colors['hp_red']
            color1 = self.colors['hp_yellow']
            ratio = min(max(self.hp_displayed / w, 0), 1)
            self.hp_color = color0.lerp(color1, ratio)
        else:
            color0 = self.colors['hp_yellow']
            color1 = self.colors['hp_green']
            ratio = min(max((self.hp_displayed - w) / w, 0), 1)
            self.hp_color = color0.lerp(color1, ratio)

    def update(self):
        if self.fade_counter == -1:
            if self.hp_displayed == self.hp:
                self.fade_counter = 0
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
    def __init__(self, fonts, colors, col=None, row=None, offset=None, letter=None):
        self.ay = 0
        self.event_timer = 5
        self.beacon = False
        self.beacon_counter = 0
        self.beacon_counter_dir = 1
        self.beacon_fade_speed = 3
        self.col = col
        self.colors = colors
        self.dims = (48, 48)
        self.first_turn = True
        self.fonts = fonts
        self.keeb_highlight = False
        self.hovered = False
        self.images = {}
        self.interactive = True
        self.marked = False
        self.middle = (0, 0)
        self.multiplier = 1
        self.paused = False
        self.point_value = 0
        self.row = row
        self.selected = False
        self.surf = pygame.Surface(self.dims)
        self.text_color = self.colors['black']
        self.tile_type = 'normal'

        self.bg_color = self.colors['beige']
        self.border_color = self.colors['light_gray']

        if offset == None:
            self.offset = 0
        else:
            self.offset = offset if self.col % 2 else (offset[0], offset[1] + (self.dims[0] / 2))

        if letter:
            self.letter = letter
        else:
            self.set_coords()
            self.set_target()
            self.choose_letter()
        self.update_point_value()
        self.set_text_color()
        self.load_images()

    def animate_beacon(self):
        self.beacon = True
        self.beacon_counter += self.beacon_fade_speed * self.beacon_counter_dir
        if self.beacon_counter > 100 or self.beacon_counter < 0:
            # Clamp values for lerp
            self.beacon_counter = min(max(self.beacon_counter, 0), 100)
            self.beacon_counter_dir *= -1
        self.bg_color = self.colors['beacon_red'].lerp(self.colors['bg_attack'], self.beacon_counter / 100.0)

        self.build_image()

    def attack_tick(self):
        self.event_timer -= 1
        if self.first_turn:
            self.first_turn = False
        else:
            if self.event_timer == 0:
                self.beacon = False
                self.keeb_highlight = False
                self.marked = False

    def build_image(self):
        # Set border color
        self.border_color = self.colors['light_gray']
        if self.hovered:
            self.border_color = self.colors['gold']
        elif self.keeb_highlight:
            self.border_color = self.colors['dark_gray']
        # Set BG color
        if not self.beacon or (self.beacon and self.selected):
            self.bg_color = self.colors[f'bg_{self.tile_type}{"_selected" if self.selected else ""}']

        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        if self.tile_type == 'stone':
            surf = pygame.Surface((self.dims[0] - 4, self.dims[1] - 4))
            surf.fill(self.bg_color)
            offset = (2, 2)
        else:
            # Render point value
            surf_pts = self.fonts['small'].render(str(format_num(self.point_value)), True, self.text_color, self.bg_color)
            # Align bottom/right
            pts_offset = tuple([self.surf.get_size()[i] - surf_pts.get_size()[i] - 3 for i in range(2)])
            self.surf.blit(surf_pts, dest=pts_offset)
            # Render letter
            surf = self.fonts['large'].render(self.letter, True, self.text_color, self.bg_color)
            # Horiz/vert align center
            offset = [floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)]
            # Bump (-1px, -4px); convert offset
            offset = tuple([offset[0], offset[1] - 4])
            # Countdown timer
            if self.tile_type == 'attack':
                surf_timer = self.fonts['small'].render(str(self.event_timer), True, self.colors['black'], self.bg_color)
                # Align bottom/left
                timer_offset = (3, self.dims[1] - surf_timer.get_size()[1] - 3)
                self.surf.blit(surf_timer, dest=timer_offset)
            elif self.tile_type == 'poison':
                surf_timer = self.fonts['small'].render(str(self.event_timer), True, self.colors['light_gray'], self.bg_color)
                # Align bottom/left
                timer_offset = (3, self.dims[1] - surf_timer.get_size()[1] - 3)
                self.surf.blit(surf_timer, dest=timer_offset)

        self.surf.blit(surf, dest=offset)

        if self.tile_type in ('attack', 'heal', 'poison'):
            self.surf.blit(self.images[self.tile_type], dest=(2, 2))

        if self.marked:
            pygame.draw.circle(self.surf, self.colors['mid_gray'], (self.dims[0] - 8, 8), 4)
            pygame.draw.circle(self.surf, self.colors['teal'], (self.dims[0] - 8, 8), 2)

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
        pop = [key for key in letter_weights]
        weights = [letter_weights[letter] for letter in pop]
        self.letter = random.choices(population=pop, weights=weights, k=1)[0]

    def get_abs_rect(self):
        return pygame.Rect(self.coords, self.dims)

    def highlight(self):
        self.keeb_highlight = True
        self.update()

    def identify(self):
        return f'c{self.col}r{self.row}'

    def load_images(self):
        for img_name in ('attack', 'heal', 'poison'):
            self.images[img_name] = pygame.image.load(os.path.join('img', img_name + '.png'))
            self.images[img_name].set_colorkey(self.colors['transparent'])

    def mouse_out(self):
        self.hovered = False
        self.border_color = self.colors['light_gray']
        self.update()

    def mouse_over(self):
        self.hovered = True
        self.border_color = self.colors['gold']
        self.update()

    def poison_tick(self):
        self.event_timer -= 1
        if self.first_turn:
            self.first_turn = False
        else:
            if self.event_timer == 0:
                self.beacon = False
                self.tile_type = 'stone'
                self.letter = '__'
                self.marked = False

    def reset(self):
        self.event_timer = 5
        self.beacon = False
        self.first_turn = True
        self.marked = False
        self.selected = False
        self.tile_type = 'normal'

        self.choose_letter()
        self.update_point_value()
        self.set_text_color()
        self.update()

    def select(self):
        self.selected = True
        self.update()

    def set_coords(self, dy=0):
        x = self.offset[0] + (self.dims[0] * self.col)
        y = self.offset[1] + (self.dims[1] * self.row) + dy

        self.coords = (x, y)
        self.set_middle()

    def set_middle(self):
        x = self.offset[0] + (self.dims[0] * self.col)
        y = self.offset[1] + (self.dims[1] * self.row)
        self.middle = (x + (self.dims[0] / 2), y + (self.dims[1] / 2))

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
        self.update()

    def unhighlight(self):
        self.keeb_highlight = False
        self.update()

    def unselect(self):
        self.selected = False
        self.update()

    def update(self, multiplier=None):
        if multiplier:
            self.multiplier = multiplier

        self.update_point_value()
        self.set_text_color()
        self.build_image()

    def update_point_value(self):
        if self.tile_type in ('heal', 'poison'):
            self.point_value = self.multiplier
        else:
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
            if self.tile_type == 'silver':
                type_multiplier = 3
            elif self.tile_type == 'gold':
                type_multiplier = 4

            self.point_value = value * self.multiplier * type_multiplier

def format_num(num):
    if num < 1000:
        return str(num)
    num = float('{:.3g}'.format(floor(num / 10) * 10))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M'][magnitude])
