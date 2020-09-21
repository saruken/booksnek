import numpy, os, pygame, random, string
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
        self.name_entry_pos = 0

        self.menu_bg = ui.Display(dims=(348, 60), coords=(-2, -2), fonts=self.fonts, colors=colors)
        coords = offset_from_element(self.menu_bg, corner=(0, 0), offset=(10, 10))
        self.menu_open = ui.Interactive(name='load', dims=(62, 40), coords=coords, fonts=self.fonts, text='LOAD', text_color='light_gray', colors=colors)
        coords = offset_from_element(self.menu_open, corner=(1, 0), offset=(4, 0))
        self.menu_save = ui.Interactive(name='save', dims=(62, 40), coords=coords, fonts=self.fonts, text='SAVE', colors=colors)
        coords = offset_from_element(self.menu_save, corner=(1, 0), offset=(4, 0))
        self.btn_clear_marked = ui.Interactive(name='clear', dims=(83, 40), coords=coords, fonts=self.fonts, text='UNMARK', enabled=False, colors=colors)
        coords = offset_from_element(self.btn_clear_marked, corner=(1, 0), offset=(4, 0))
        self.btn_scramble = ui.Interactive(name='scramble', dims=(109, 40), coords=coords, colors=colors, fonts=self.fonts, text='SCRAMBLE', text_color='light_gray')
        coords = offset_from_element(self.menu_bg, corner=(0, 1), offset=(12, 10))
        self.bonus_display = ui.Display(dims=(336, 40), coords=coords, fonts=self.fonts, colors=colors, text_color='light_gray', label='MULTIPLIER+', center=True)
        coords = offset_from_element(self.bonus_display, corner=(0, 1), offset=(0, 10))
        self.hp_display = ui.HPDisplay(dims=(336, 34), coords=coords, fonts=self.fonts, colors=colors)
        coords = offset_from_element(self.hp_display, corner=(0, 1), offset=(0, 10))
        self.level_display = ui.Display(dims=(246, 40), coords=coords, fonts=self.fonts, colors=colors, label='LEVEL / EXP: ', text_prefix='Lv. ', text_color='light_gray', center=True, show_progress=True)
        coords = offset_from_element(self.level_display, corner=(1, 0), offset=(10, 0))
        self.multiplier_display = ui.Display(dims=(80, 40), coords=coords, fonts=self.fonts, colors=colors, label='MULT.', text_prefix='x', text_color='light_gray', center=True)
        coords = offset_from_element(self.menu_bg, corner=(1, 0), offset=(10, 10))
        self.score_display = ui.Display(dims=(243, 40), coords=coords, fonts=self.fonts, colors=colors, text='0', text_color='light_gray', label='SCORE', center=True)
        coords = offset_from_element(self.score_display, corner=(1, 0), offset=(4, 0))
        self.menu_quit = ui.Interactive(name='quit', dims=(63, 40), coords=coords, fonts=self.fonts, text='QUIT', colors=colors, text_color='light_gray')
        coords = offset_from_element(self.score_display, corner=(0, 1), offset=(0, 4))
        self.word_display = ui.Display(dims=(310, 40), coords=coords, fonts=self.fonts, colors=colors, text_color='light_gray', label="SELECTED", center=True)
        coords = offset_from_element(self.word_display, corner=(0, 1), offset=(0, 4))
        self.longest_display = ui.Display(dims=(310, 34), coords=coords, fonts=self.fonts, colors=colors, label='LONGEST WORD', text_color='beige', center=True)
        coords = offset_from_element(self.longest_display, corner=(0, 1), offset=(0, 4))
        self.best_display = ui.Display(dims=(310, 34), coords=coords, fonts=self.fonts, colors=colors, label='HIGHEST SCORE', text_color='beige', center=True, text_offset=(30, 2), multicolor=True)
        coords = offset_from_element(self.best_display, corner=(0, 1), offset=(0, 4))
        self.history_display = ui.Display(dims=(310, 292), coords=coords, fonts=self.fonts, colors=colors, label='WORD LIST')
        coords = offset_from_element(self.history_display, corner=(0, 1), offset=(0, 4))
        self.hi_score_display = ui.Display(dims=(310, 125), coords=coords, fonts=self.fonts, colors=colors, label='HI SCORES')

        self.gfx = GFXSurf(self.fonts, colors)

        self.splash_elements = []
        self.ui_elements = []
        self.menu_btns = [self.menu_open, self.menu_save, self.btn_clear_marked, self.btn_scramble, self.menu_quit]
        self.game_elements = [self.bonus_display, self.hp_display, self.score_display, self.word_display, self.history_display, self.hi_score_display, self.longest_display, self.best_display, self.level_display, self.multiplier_display, self.menu_bg, self.menu_quit, self.menu_open, self.menu_save, self.btn_clear_marked, self.btn_scramble]

    def advance_tutorial(self):
        self.tutorial_current_step += 1
        self.show_gif()
        self.splash_elements[2].set_text(self.tutorial_steps[self.tutorial_current_step])

        if self.tutorial_current_step == len(self.tutorial_steps) - 1:
            self.splash_elements.pop(3) # Remove 'Next' button

    def clear_name(self):
        self.name_entry_pos = 0
        self.create_name_menu('')

    def create_game_over_menu(self):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('GAME OVER', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        surf_dims = (284, 120)
        menu_bg = ui.Display(dims=surf_dims, coords=(38, 290), fonts=self.fonts, colors=self.colors)
        menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        coords = offset_from_element(menu_bg, corner=(0, 0), offset=(0, 60))
        btn = ui.Interactive(name='game over ok', dims=(63, 40), coords=(149, coords[1]), fonts=self.fonts, text='OK', colors=self.colors, text_color='light_gray')
        self.splash_elements = [menu_bg, btn]

    def create_game_saved_menu(self, id):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('GAME SAVED AS:', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        surf_dims = (304, 140)
        menu_bg = ui.Display(dims=surf_dims, coords=(18, 290), fonts=self.fonts, colors=self.colors)
        menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        id_text = self.fonts['medium'].render(id, True, self.colors['bg_gold'], None)
        w = id_text.get_size()[0]
        h = header.get_size()[1]
        menu_bg.surf.blit(id_text, dest=(surf_dims[0] / 2 - w / 2, 20 + h))
        btn = ui.Interactive(name='game saved ok', dims=(64, 40), coords=(136, 380), fonts=self.fonts, text='OK', colors=self.colors, text_color='light_gray')
        self.splash_elements = [menu_bg, btn]

    def create_invalid_word_menu(self, word):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('INVALID WORD:', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        surf_dims = (304, 140)
        menu_bg = ui.Display(dims=surf_dims, coords=(18, 290), fonts=self.fonts, colors=self.colors)
        menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        text = self.fonts['medium'].render(word, True, self.colors['red'], None)
        w = text.get_size()[0]
        h = header.get_size()[1]
        menu_bg.surf.blit(text, dest=(surf_dims[0] / 2 - w / 2, 20 + h))
        btn = ui.Interactive(name='invalid word ok', dims=(64, 40), coords=(136, 380), fonts=self.fonts, text='OK', colors=self.colors, text_color='light_gray')
        self.splash_elements = [menu_bg, btn]

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

    def create_name_menu(self, player_name):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('PLAYER NAME', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        surf_dims = (350, 200)
        menu_bg = ui.Display(dims=surf_dims, coords=(163, 90), fonts=self.fonts, colors=self.colors)
        menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        coords = offset_from_element(menu_bg, corner=(1, 1), offset=(-150, -50))
        btn_start = ui.Interactive(name='name start', dims=(140, 40), coords=coords, fonts=self.fonts, text='START', colors=self.colors, text_color='light_gray')
        coords = offset_from_element(menu_bg, corner=(0, 1), offset=(10, -50))
        btn_clear = ui.Interactive(name='name clear', dims=(140, 40), coords=coords, fonts=self.fonts, text='CLEAR', colors=self.colors, text_color='light_gray')
        if self.name_entry_pos >= len(player_name):
            tile_surf = pygame.Surface(((len(player_name) + 1) * 48, 48))
        else:
            tile_surf = pygame.Surface((len(player_name) * 48, 48))
        for n, letter in enumerate(player_name):
            tile = ui.Tile(fonts=self.fonts, colors=self.colors, letter=letter)
            if n == self.name_entry_pos:
                tile.mouse_over()
            else:
                tile.mouse_out()
            tile_surf.blit(tile.surf, dest=(n * 48, 0))
        if self.name_entry_pos >= len(player_name):
            border = pygame.Surface((48, 48))
            border.fill(self.colors['gold'])
            pygame.draw.rect(border, self.colors['bg_main'], pygame.Rect((2, 2), (44, 44)))
            tile_surf.blit(border, dest=(len(player_name) * 48, 0))

        w = tile_surf.get_size()[0]
        menu_bg.surf.blit(tile_surf, dest=(175 - w / 2, 50))
        self.splash_elements = [menu_bg, btn_start, btn_clear]

    def create_quit_menu(self):
        self.hide_splash_menu()
        header = self.fonts['medium'].render('REALLY QUIT?', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        surf_dims = (284, 140)
        quit_menu_bg = ui.Display(dims=surf_dims, coords=(38, 290), fonts=self.fonts, colors=self.colors)
        quit_menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        coords = offset_from_element(quit_menu_bg, corner=(0, 0), offset=(10, 60))
        quit_menu_no = ui.Interactive(name='quit no', dims=(127, 40), coords=coords, fonts=self.fonts, text='NO', colors=self.colors, text_color='light_gray')
        coords = offset_from_element(quit_menu_bg, corner=(1, 0), offset=(-137, 60))
        quit_menu_yes = ui.Interactive(name='quit yes', dims=(127, 40), coords=coords, fonts=self.fonts, text='YES', colors=self.colors, text_color='light_gray')
        self.splash_elements = [quit_menu_bg, quit_menu_no, quit_menu_yes]

    def create_splash_menu(self, scores):
        self.hide_splash_menu()

        # Load / Tutorial / New Game menu
        header = self.fonts['medium'].render('WELCOME TO BOOKSNEK!', True, self.colors['light_gray'], None)
        w = header.get_size()[0]
        surf_dims = (284, 160)
        splash_menu_bg = ui.Display(dims=surf_dims, coords=(196, 10), fonts=self.fonts, colors=self.colors)
        splash_menu_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        coords = offset_from_element(splash_menu_bg, corner=(0, 0), offset=(10, 60))
        splash_menu_open = ui.Interactive(name='splash load', dims=(127, 40), coords=coords, fonts=self.fonts, text='LOAD', colors=self.colors, text_color='light_gray')
        coords = offset_from_element(splash_menu_open, corner=(1, 0), offset=(10, 0))
        splash_menu_tutorial = ui.Interactive(name='splash tutorial', dims=(127, 40), coords=coords, fonts=self.fonts, text='TUTORIAL', text_color='light_gray', colors=self.colors)
        coords = offset_from_element(splash_menu_open, corner=(0, 1), offset=(0, 10))
        splash_menu_new = ui.Interactive(name='splash new', dims=(264, 40), coords=coords, fonts=self.fonts, text='NEW GAME', text_color='light_gray', colors=self.colors)

        # Hi Score list
        header = self.fonts['medium'].render('~ HI SCORES ~', True, self.colors['bg_gold'], None)
        w = header.get_size()[0]
        surf_dims = (656, 387)
        coords = offset_from_element(splash_menu_bg, corner=(0, 1), offset=(0, 40))
        scores_bg = ui.Display(dims=surf_dims, coords=(10, coords[1]), fonts=self.fonts, colors=self.colors)
        scores_bg.surf.blit(header, dest=(surf_dims[0] / 2 - w / 2, 10))
        label = self.fonts['medium'].render('Name', True, self.colors['mid_gray'], None)
        scores_bg.surf.blit(label, dest=(66, 60))
        label = self.fonts['medium'].render('Level', True, self.colors['mid_gray'], None)
        scores_bg.surf.blit(label, dest=(388, 60))
        label = self.fonts['medium'].render('Score', True, self.colors['mid_gray'], None)
        scores_bg.surf.blit(label, dest=(550, 60))
        for n, entry in enumerate(scores):
            color = self.colors['gold'] if entry['current'] else self.colors['light_gray']
            val = self.fonts['medium'].render(f'{str(n + 1)}.', True, color, None)
            scores_bg.surf.blit(val, dest=(10, 108 + n * 48 + n * 10))
            for i, letter in enumerate(entry['username']):
                tile = ui.Tile(fonts=self.fonts, colors=self.colors, letter=letter)
                tile.mouse_out()
                scores_bg.surf.blit(tile.surf, dest=(34 + i * 48, 86 + n * 48 + n * 10))
            val = self.fonts['medium'].render(str(entry['level']), True, color, None)
            scores_bg.surf.blit(val, dest=(400, 110 + n * 48 + n * 10))
            val = self.fonts['medium'].render('{:,}'.format(entry['score']), True, color, None)
            w = val.get_size()[0]
            scores_bg.surf.blit(val, dest=(636 - w, 110 + n * 48 + n * 10))

        self.splash_elements = [splash_menu_bg, splash_menu_open, splash_menu_tutorial, splash_menu_new, scores_bg]

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

    def is_neighbor(self, new_tile, old_tile):

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

    def show_gif(self):
        # TODO: Load & display self.tutorial_gifs[self.tutorial_current_step]
        pass

    def update_hi_score_display(self, scores):
        self.hi_score_display.update()
        for n, entry in enumerate(scores):
            color = self.colors['bg_gold'] if entry['current'] else self.colors['light_gray']
            surf = self.fonts['medium'].render(f'{n + 1}. {entry["username"]}', True, color)
            h = surf.get_size()[1]
            self.hi_score_display.surf.blit(surf, dest=(10, 14 + h * n + 5 * n))
            score = '{:,}'.format(entry['score'])
            surf = self.fonts['medium'].render(score, True, color)
            w = surf.get_size()[0]
            pos_x = self.hi_score_display.surf.get_size()[0] - 10 - w
            self.hi_score_display.surf.blit(surf, dest=(pos_x, 12 + h * n + 4 * n))

    def update_name(self, player_name, letter):
        name = list(player_name)
        if letter not in string.ascii_uppercase:
            if letter == 'RIGHT':
                if self.name_entry_pos < 4:
                    try:
                        name[self.name_entry_pos]
                        self.name_entry_pos += 1
                    except IndexError:
                        pass
                    new_name = player_name
            elif letter == 'LEFT':
                if self.name_entry_pos:
                    self.name_entry_pos -= 1
                new_name = player_name
            elif letter == 'BACKSPACE':
                if self.name_entry_pos:
                    name[self.name_entry_pos - 1] = ''
                    name.pop(self.name_entry_pos - 1)
                    self.name_entry_pos -= 1
                    new_name = ''.join(name)
                else:
                    new_name = player_name
            elif letter == 'DELETE':
                if self.name_entry_pos < len(name):
                    name[self.name_entry_pos] = ''
                    name.pop(self.name_entry_pos)
                    new_name = ''.join(name)
                else:
                    new_name = player_name
            else:
                new_name = player_name
            self.create_name_menu(new_name)
            return new_name
        try:
            name[self.name_entry_pos] = letter
        except IndexError:
            name.append(letter)
        if self.name_entry_pos < 4:
            self.name_entry_pos += 1
        new_name = ''.join(name)
        self.create_name_menu(new_name)
        return new_name

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
                if g['motion'] == 'rise':
                    g['vx'] += g['vx_accel']
                    g['vy'] -= g['vy_accel']
                    g['offset_x'] += g['vx'] * step
                    g['offset_y'] += g['vy'] * step
                elif g['motion'] == 'burst':
                    g['vx'] *= 0.985
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
                offset_x -= 10
            else:
                color = self.colors['green']
                prefix = '+'
                offset_x += 10
            surf = self.fonts['large'].render(prefix + str(amt), True, color)
        print(f'Creating delta with offset_x={offset_x}')
        delta = {
            'dims': surf.get_size(),
            'fade_counter': 255 + random.choice(range(50)),
            'fade_step': 1.5,
            'offset_x': offset_x - (surf.get_size()[0] / 2),
            'offset_y': 130 - surf.get_size()[1],
            'motion': 'rise',
            'surf': surf,
            'vx': 0,
            'vx_accel': 0,
            'vy': 0,
            'vy_accel': 0.001
        }

        self.gfx.append(delta)

    def create_ghost(self, tile, ghost_color, motion='rise', direction=None):
        surf = pygame.Surface(tile.dims)
        surfarray = pygame.surfarray.array2d(tile.surf)
        transparent_c = surf.map_rgb(self.colors['transparent'])
        wireframe = numpy.full_like(surfarray, transparent_c)
        bg_c = surf.map_rgb(tile.bg_color)
        wireframe_c = surf.map_rgb(ghost_color)
        wireframe = numpy.array([[transparent_c if c == bg_c else wireframe_c for c in row] for row in surfarray])
        pygame.surfarray.blit_array(surf, wireframe)
        surf.set_colorkey(self.colors['transparent'])
        vx = 0
        vy = 0
        amt = .6
        if motion == 'burst':
            if direction == 'n':
                vy = -amt * 2 + (random.choice(range(5)) - 2) / 100
            elif direction == 'ne':
                vx = amt + (random.choice(range(5)) - 2) / 100
                vy = -amt + (random.choice(range(5)) - 2) / 100
            elif direction == 'se':
                vx = amt + (random.choice(range(5)) - 2) / 100
                vy = amt + (random.choice(range(5)) - 2) / 100
            elif direction == 's':
                vy = amt * 2 + (random.choice(range(5)) - 2) / 100
            elif direction == 'sw':
                vx = -amt + (random.choice(range(5)) - 2) / 100
                vy = amt + (random.choice(range(5)) - 2) / 100
            elif direction == 'nw':
                vx = -amt + (random.choice(range(5)) - 2) / 100
                vy = -amt + (random.choice(range(5)) - 2) / 100
        ghost = {
            'fade_counter': 200 + random.choice(range(155)),
            'fade_step': 3,
            'offset_x': tile.coords[0],
            'offset_y': tile.coords[1],
            'motion': motion,
            'surf': surf,
            'vx': vx,
            'vx_accel': (random.choice(range(3)) - 1) / 100,
            'vy': vy,
            'vy_accel': 0.03 + ((random.choice(range(5)) - 2) / 100)
        }
        self.gfx.append(ghost)

    def draw_arcs(self, arc_sources):
        for source in arc_sources:
            arc_start = source[0]
            if source[3] == 'HP':
                arc_end = (150 + source[4], 136)
            elif source[3] == 'HP_MAX':
                arc_end = (204, 136)
            pts = [arc_start, arc_end]
            left = min(pts[0][0], pts[1][0])
            top = min(pts[0][1], pts[1][1])
            width = max((max(pts[0][0], pts[1][0]) - min(pts[0][0], pts[1][0])) * 2, 20)
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
                'motion': None,
                'surf': surf,
                'vx': 0,
                'vx_accel': 0,
                'vy': 0,
                'vy_accel': 0
            }
            pygame.draw.arc(surf, color, pygame.Rect(left, top, width, height), start_angle, stop_angle, width=3)
            print(f'Drew arc: l={left}, t={top}, w={width}, h={height}, c={color}')
            self.gfx.append(arc)

            self.create_delta(amt=source[2], offset_x=arc_end[0])

def offset_from_element(element, corner, offset):
    point = [element.coords[i] + element.surf.get_size()[i] if corner[i] else element.coords[i] for i in range(len(corner))]
    return tuple([point[i] + offset[i] for i in range(len(point))])
