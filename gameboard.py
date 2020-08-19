import numpy, pygame, random
from math import pi
from time import sleep

import ui

class Board():
    def __init__(self, dims, coords, colors):
        self.background = pygame.Surface(dims)
        self.background.fill(colors['bg_back'])
        self.coords = coords
        self.fonts = {
            'large': pygame.font.Font('VCR_OSD_MONO.ttf', 36),
            'medium': pygame.font.Font('VCR_OSD_MONO.ttf', 18),
            'small': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }

        self.menu_bg = ui.Display(dims=(348, 60), coords=(-2, -2), fonts=self.fonts, colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 0), offset=(10, 10))
        self.menu_new = ui.Interactive(name='new', dims=(52, 40), coords=coords, fonts=self.fonts, text='NEW', colors=colors, text_color='light_gray')
        coords = offset_from_element(self.menu_new, corner=(1, 0), offset=(10, 0))
        self.menu_open = ui.Interactive(name='open', dims=(63, 40), coords=coords, fonts=self.fonts, text='LOAD', text_color='light_gray', colors=colors)
        coords = offset_from_element(self.menu_open, corner=(1, 0), offset=(10, 0))
        self.menu_save = ui.Interactive(name='save', dims=(63, 40), coords=coords, fonts=self.fonts, text='SAVE', enabled=False, colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 1), offset=(12, 10))
        self.bonus_display = ui.Display(dims=(336, 40), coords=coords, fonts=self.fonts, colors=colors, text_color='light_gray', label='MULTIPLIER+', center=True)
        coords = offset_from_element(self.bonus_display, corner=(0, 1), offset=(0, 10))
        self.hp_display = ui.HPDisplay(dims=(336, 34), coords=coords, fonts=self.fonts, colors=colors)
        coords = offset_from_element(self.hp_display, corner=(0, 1), offset=(0, 10))
        self.level_display = ui.Display(dims=(136, 40), coords=coords, fonts=self.fonts, colors=colors, label='EXP.', text_prefix='Lv', text_color='light_gray', center=True, show_progress=True)
        coords = offset_from_element(self.level_display, corner=(1, 0), offset=(10, 0))
        self.multiplier_display = ui.Display(dims=(80, 40), coords=coords, fonts=self.fonts, colors=colors, label='MULT.', text_prefix='x', text_color='light_gray', center=True)
        coords = offset_from_element(self.multiplier_display, corner=(1, 0), offset=(10, 0))
        self.btn_clear_marked = ui.Interactive(name='clear', dims=(100, 40), coords=coords, fonts=self.fonts, text='UNMARK', enabled=False, colors=colors)
        coords = offset_from_element(self.menu_save, corner=(1, 0), offset=(10, 0))
        self.btn_scramble = ui.Interactive(name='scramble', dims=(120, 40), coords=coords, colors=colors, fonts=self.fonts, text='SCRAMBLE', text_color='light_gray')
        coords = offset_from_element(self.btn_scramble, corner=(1, 0), offset=(20, 0))
        self.score_display = ui.Display(dims=(310, 40), coords=coords, fonts=self.fonts, colors=colors, text='0', text_color='light_gray', label='SCORE', center=True)
        coords = offset_from_element(self.score_display, corner=(0, 1), offset=(0, 4))
        self.word_display = ui.Display(dims=(310, 40), coords=coords, fonts=self.fonts, colors=colors, text_color='light_gray', label="SELECTED", center=True)
        coords = offset_from_element(self.word_display, corner=(0, 1), offset=(0, 4))
        self.longest_display = ui.Display(dims=(310, 34), coords=coords, fonts=self.fonts, colors=colors, label='LONGEST WORD', text_color='beige', center=True)
        coords = offset_from_element(self.longest_display, corner=(0, 1), offset=(0, 4))
        self.best_display = ui.Display(dims=(310, 34), coords=coords, fonts=self.fonts, colors=colors, label='HIGHEST SCORE', text_color='beige', center=True, text_offset=(30, 2), multicolor=True)
        coords = offset_from_element(self.best_display, corner=(0, 1), offset=(0, 4))
        self.history_display = ui.Display(dims=(310, 425), coords=coords, fonts=self.fonts, colors=colors, label='WORD LIST')

        self.deltas = DeltaSurf(self.fonts, colors)
        self.gfx = GFXSurf(colors)

        self.menu_btns = [self.btn_clear_marked, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]
        self.ui_elements = [self.bonus_display, self.hp_display, self.score_display, self.word_display, self.history_display, self.longest_display, self.best_display, self.level_display, self.multiplier_display, self.btn_clear_marked, self.menu_bg, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]

    def create_tiles(self, colors, offset):
        tiles = []
        # Every other column has 7 and 8 tiles, starting and ending with 7s
        for col in range(7):
            for row in range(7 + col % 2):
                tiles.append(ui.Tile(fonts=self.fonts, col=col, row=row, colors=colors, offset=offset))

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

class DeltaSurf:
    def __init__(self, fonts, colors):
        self.colors = colors
        self.coords = (30, 150)
        self.deltas = []
        self.fonts = fonts
        self.interactive = False

    def add(self, amt):
        if amt < 0:
            color = self.colors['red']
            prefix = ''
        else:
            color = self.colors['green']
            prefix = '+'
        surf = self.fonts['large'].render(prefix + str(amt), True, color)
        offset_x = random.choice(range(250))
        offset_y = 0
        delta = {
            'color': color,
            'dims': surf.get_size(),
            'fade_counter': 255 + random.choice(range(100)),
            'offset_x': offset_x,
            'offset_y': offset_y,
            'surf': surf
        }
        self.deltas.append(delta)

    def blit_deltas(self, window_surface):
        for i, d in enumerate(self.deltas):
            d['fade_counter'] -= 1
            if d['fade_counter'] > 0:
                d['offset_y'] -= 20 / d['fade_counter']
                d['surf'].set_alpha(d['fade_counter'])
                dest = (self.coords[0] + d['offset_x'], self.coords[1] - d['dims'][1] + d['offset_y'])
                window_surface.blit(d['surf'], dest=dest)
            else:
                self.deltas.pop(i)

class GFXSurf:
    def __init__(self, colors):
        self.colors = colors
        self.fps = 0
        self.gfx = []
        self.interactive = False

    def blit_gfx(self, window_surface):
        step = (self.fps / 60)

        for g in self.gfx:
            g['fade_counter'] = max(0, g['fade_counter'] - g['fade_step'] * step)
            if g['fade_counter'] > 0:
                if g['rise']:
                    g['vx'] += g['vx_accel']
                    g['vy'] -= g['vy_accel']
                    g['offset_x'] += g['vx'] * step
                    g['offset_y'] += g['vy'] * step
                g['surf'].set_alpha(g['fade_counter'])
                dest = (g['offset_x'], g['offset_y'])
                window_surface.blit(g['surf'], dest=dest)
        if not [g for g in self.gfx if g['fade_counter'] > 0]:
            self.gfx = []

    def create_ghost(self, tile, ghost_color):
        surf = pygame.Surface(tile.dims)
        surfarray = pygame.surfarray.array3d(tile.surf)
        masked = surfarray.copy()
        bg_color = [tile.bg_color.r, tile.bg_color.g, tile.bg_color.b]
        ghost_color_array = [ghost_color.r, ghost_color.g, ghost_color.b]
        for r, row in enumerate(masked):
            for p, px in enumerate(row):
                if (px == bg_color).all():
                    masked[r][p] = [255, 0, 255] # Set px to purple
                else:
                    masked[r][p] = ghost_color_array
        pygame.surfarray.blit_array(surf, masked)
        surf.set_colorkey(self.colors['transparent'])
        ghost = {
            'fade_counter': 200 + random.choice(range(155)),
            'fade_step': 3,
            'offset_x': tile.coords[0],
            'offset_y': tile.coords[1],
            'rise': True,
            'surf': surf,
            'vx': 0,
            'vx_accel': (random.choice(range(3)) - 1) / 100,
            'vy': 0,
            'vy_accel': 0.03 + ((random.choice(range(5)) - 2) / 100)
        }
        self.gfx.append(ghost)

    def draw_arcs(self, arc_sources):
        for source in arc_sources:
            arc_start = source[0]
            arc_end = (100 + random.choice(range(100)), 136)
            pts = [arc_start, arc_end]
            left = min(pts[0][0], pts[1][0])
            top = min(pts[0][1], pts[1][1])
            width = (max(pts[0][0], pts[1][0]) - min(pts[0][0], pts[1][0])) * 2
            height = (max(pts[0][1], pts[1][1]) - min(pts[0][1], pts[1][1])) * 2
            if pts[0][0] < pts[1][0]:
                start_angle = pi/2
                stop_angle = pi
            else:
                left -= width / 2
                start_angle = 0
                stop_angle = pi/2
            color = self.colors[source[1]]

            surf = pygame.Surface((700, 700))
            surf.fill(self.colors['transparent'])
            surf.set_colorkey(self.colors['transparent'])
            arc = {
                'fade_counter': 255 + random.choice(range(100)),
                'fade_step': 2,
                'offset_x': 0,
                'offset_y': 0,
                'rise': False,
                'surf': surf,
                'vx': 0,
                'vx_accel': 0,
                'vy': 0,
                'vy_accel': 0
            }
            pygame.draw.arc(surf, color, pygame.Rect(left, top, width, height), start_angle, stop_angle, width=3)
            self.gfx.append(arc)

def offset_from_element(element, corner, offset):
    point = [element.coords[i] + element.surf.get_size()[i] if corner[i] else element.coords[i] for i in range(len(corner))]
    return tuple([point[i] + offset[i] for i in range(len(point))])
