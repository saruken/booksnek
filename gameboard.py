import numpy, os, pygame, random
from math import pi
from time import sleep

import ui

class Board():
    def __init__(self, dims, coords, colors):
        self.background = pygame.Surface(dims)
        self.background.fill(colors['bg_back'])
        self.colors = colors
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
        self.menu_open = ui.Interactive(name='load', dims=(63, 40), coords=coords, fonts=self.fonts, text='LOAD', text_color='light_gray', colors=colors)
        coords = offset_from_element(self.menu_open, corner=(1, 0), offset=(10, 0))
        self.menu_save = ui.Interactive(name='save', dims=(63, 40), coords=coords, fonts=self.fonts, text='SAVE', colors=colors)
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

        self.gfx = GFXSurf(self.fonts, colors)

        self.splash_elements = []
        self.ui_elements = []
        self.menu_btns = [self.btn_clear_marked, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]
        self.game_elements = [self.bonus_display, self.hp_display, self.score_display, self.word_display, self.history_display, self.longest_display, self.best_display, self.level_display, self.multiplier_display, self.btn_clear_marked, self.menu_bg, self.menu_new, self.menu_open, self.menu_save, self.btn_scramble]
        self.create_splash_menu()

    def advance_tutorial(self):
        self.tutorial_current_step += 1
        self.show_gif()
        self.splash_elements[2].set_text(self.tutorial_steps[self.tutorial_current_step])

        if self.tutorial_current_step == len(self.tutorial_steps) - 1:
            self.splash_elements.pop(3) # Remove 'Next' button

    def create_load_menu(self, gamestates):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('LOAD GAMESTATE', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        h = header.get_size()[1]
        surf_dims = (400, 400)
        load_menu_bg = ui.Display(dims=surf_dims, coords=(138, 60), fonts=self.fonts, colors=self.colors)
        load_menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        btn_back = ui.Interactive(name='load back', dims=(63, 40), coords=(10, 558), fonts=self.fonts, text='BACK', text_color='light_gray', colors=self.colors)
        gamestate_btns = []

        coords = offset_from_element(load_menu_bg, corner=(0, 0), offset=(10, 20 + h))
        if gamestates:
            for n, gamestate in enumerate(gamestates):
                username = gamestate['username'] if gamestate['username'] else 'SNEK'
                game_id = gamestate['username'] + ' ' + gamestate['timestamp']
                btn = ui.Interactive(name=f'gamestate {gamestate["id"]}', dims=(380, 40), coords=coords, fonts=self.fonts, text=game_id, colors=self.colors, text_color='light_gray')
                coords = (coords[0], coords[1] + 50)
                gamestate_btns.append(btn)
        else:
            btn = ui.Display(dims=(264, 40), coords=coords, fonts=self.fonts, text='NO SAVED GAMESTATES', colors=self.colors, center=True)
            gamestate_btns.append(btn)
        self.splash_elements = [load_menu_bg, btn_back] + gamestate_btns

    def create_splash_menu(self):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('WELCOME TO BOOKSNEK!', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        h = header.get_size()[1]
        surf_dims = (284, 160)
        splash_menu_bg = ui.Display(dims=surf_dims, coords=(196, 204), fonts=self.fonts, colors=self.colors)
        splash_menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        coords = offset_from_element(splash_menu_bg, corner=(0, 0), offset=(10, 60))
        splash_menu_open = ui.Interactive(name='splash load', dims=(127, 40), coords=coords, fonts=self.fonts, text='LOAD', colors=self.colors, text_color='light_gray')
        coords = offset_from_element(splash_menu_open, corner=(1, 0), offset=(10, 0))
        splash_menu_tutorial = ui.Interactive(name='splash tutorial', dims=(127, 40), coords=coords, fonts=self.fonts, text='TUTORIAL', text_color='light_gray', colors=self.colors)
        coords = offset_from_element(splash_menu_open, corner=(0, 1), offset=(0, 10))
        splash_menu_new = ui.Interactive(name='splash new', dims=(264, 40), coords=coords, fonts=self.fonts, text='NEW GAME', text_color='light_gray', colors=self.colors)

        self.splash_elements = [splash_menu_bg, splash_menu_open, splash_menu_tutorial, splash_menu_new]

    def create_tiles(self, colors, offset):
        tiles = []
        # Columns alternate between 7 and 8 tiles, starting and ending with 7s
        for col in range(7):
            for row in range(7 + col % 2):
                tiles.append(ui.Tile(fonts=self.fonts, col=col, row=row, colors=colors, offset=offset))

        return tiles

    def create_tutorial(self):
        self.tutorial_steps = ['Connect adjacent letters to form a word', 'Creating valid words yields points and EXP']
        self.tutorial_gifs = [None for t in self.tutorial_steps]
        self.tutorial_current_step = 0
        self.hide_splash_menu()
        header = self.fonts['medium'].render('BOOKSNEK TUTORIAL', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        h = header.get_size()[1]
        surf_dims = (656, 588)
        tutorial_text = self.tutorial_steps[self.tutorial_current_step]
        tut_menu_bg = ui.Display(dims=surf_dims, coords=(10, 10), fonts=self.fonts, colors=self.colors)
        tut_menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        demo_bg = ui.Display(dims=(328, 294), coords=(178, 30 + h), fonts=self.fonts, colors=self.colors, label="DEMO", text="GIF HERE", center=True)
        coords = offset_from_element(demo_bg, corner=(0, 1), offset=(0, 10))
        display = ui.Display(dims=(surf_dims[0] - 20, 20 + h), coords=(20, coords[1]), fonts=self.fonts, colors=self.colors, text_color='light_gray', label="SNEK TIP", text=tutorial_text, text_offset=(8, 10), vert_center=False)
        coords = offset_from_element(tut_menu_bg, corner=(1, 1), offset=(-73, -50))
        btn_next = ui.Interactive(name='tutorial next', dims=(63, 40), coords=coords, fonts=self.fonts, text='NEXT', text_color='light_gray', colors=self.colors)
        coords = offset_from_element(tut_menu_bg, corner=(0, 1), offset=(10, -50))
        btn_done = ui.Interactive(name='tutorial done', dims=(63, 40), coords=coords, fonts=self.fonts, text='DONE', text_color='light_gray', colors=self.colors)

        self.splash_elements = [tut_menu_bg, demo_bg, display, btn_next, btn_done]

    def hide_splash_menu(self):
        for elem in self.splash_elements:
            self.surf = None
            elem = None
        self.splash_elements = []

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

    def show_gif(self):
        # TODO: Load & display self.tutorial_gifs[self.tutorial_current_step]
        pass

class GFXSurf:
    def __init__(self, fonts, colors):
        self.colors = colors
        self.fonts = fonts
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

    def create_delta(self, amt, offset_x):
        if type(amt) == str:
            color = self.colors['gold']
            prefix = '+'
            surf = self.fonts['medium'].render(prefix + amt, True, color)
        else:
            if amt < 0:
                color = self.colors['red']
                prefix = ''
            else:
                color = self.colors['green']
                prefix = '+'
            surf = self.fonts['large'].render(prefix + str(amt), True, color)
        delta = {
            'dims': surf.get_size(),
            'fade_counter': 255 + random.choice(range(50)),
            'fade_step': 2,
            'offset_x': offset_x - (surf.get_size()[0] / 2),
            'offset_y': 130 - surf.get_size()[1],
            'rise': True,
            'surf': surf,
            'vx': 0,
            'vx_accel': 0,
            'vy': 0,
            'vy_accel': 0.003
        }

        self.gfx.append(delta)

    def create_ghost(self, tile, ghost_color):
        surf = pygame.Surface(tile.dims)
        surfarray = pygame.surfarray.array2d(tile.surf)
        transparent_c = surf.map_rgb(pygame.Color('#ff00ff'))
        wireframe = numpy.full_like(surfarray, transparent_c)
        bg_c = surf.map_rgb(tile.bg_color)
        wireframe_c = surf.map_rgb(ghost_color)
        wireframe = numpy.array([[transparent_c if c == bg_c else wireframe_c for c in row] for row in surfarray])
        pygame.surfarray.blit_array(surf, wireframe)
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

            self.create_delta(amt=source[2], offset_x=arc_end[0])

def offset_from_element(element, corner, offset):
    point = [element.coords[i] + element.surf.get_size()[i] if corner[i] else element.coords[i] for i in range(len(corner))]
    return tuple([point[i] + offset[i] for i in range(len(point))])
