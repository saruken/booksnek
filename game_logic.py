import json, pygame, random, threading
from datetime import datetime
from math import ceil, floor
from numpy.random import choice

import gameboard, tile_snake
from ui import Interactive, Tile

class Game:
    def __init__(self, dims, dictionary):
        self.colors = {
            'attack': pygame.Color('#ad3e3e'),
            'beige': pygame.Color('#aaaa66'),
            'bg_attack': pygame.Color('#e05a41'),
            'bg_attack_selected': pygame.Color('#e37c68'),
            'bg_back': pygame.Color('#38424d'),
            'bg_gold': pygame.Color('#ebc334'),
            'bg_gold_selected': pygame.Color('#fcde72'),
            'bg_heal': pygame.Color('#349eeb'),
            'bg_heal_selected': pygame.Color('#76bff5'),
            'bg_main': pygame.Color('#21282d'),
            'bg_normal': pygame.Color('#c1a663'),
            'bg_normal_selected': pygame.Color('#f0d081'),
            'bg_poison': pygame.Color('#3b3245'),
            'bg_poison_selected': pygame.Color('#655775'),
            'bg_progress': pygame.Color('#161a1c'),
            'bg_silver': pygame.Color('#9eadad'),
            'bg_silver_selected': pygame.Color('#d5e7e8'),
            'bg_stone': pygame.Color('#5f666b'),
            'beacon_red': pygame.Color('#ab2200'),
            'black': pygame.Color('#000000'),
            'border_gold': pygame.Color('#d4c413'),
            'dark_gray': pygame.Color('#202d36'),
            'gold': pygame.Color('#fce803'),
            'green': pygame.Color('#65a669'),
            'hp_green': pygame.Color('#305431'),
            'hp_red': pygame.Color('#b3281e'),
            'hp_yellow': pygame.Color('#d16411'),
            'light_gray': pygame.Color('#bfb9a8'),
            'mid_gray': pygame.Color('#546c7a'),
            'ocean': pygame.Color('#244254'),
            'poison': pygame.Color('#7c6e8a'),
            'poison_bright': pygame.Color('#bb60f0'),
            'progress': pygame.Color('#c9c618'),
            'red': pygame.Color('#e05a41'),
            'silver': pygame.Color('#d5e7e8'),
            'teal': pygame.Color('#50aef2'),
            'transparent': pygame.Color('#ff00ff')
        }

        self.animating = False
        self.board = gameboard.Board(dims=dims, coords=(0, 0), colors=self.colors)
        self.dictionary = dictionary
        self.hi_scores = self.load_hi_scores()
        self.uncurrent_hi_scores()
        self.max_history_words = 17
        self.mode = 'menu'
        self.player_name = 'SNEK'
        self.snake = tile_snake.Snake()
        tile_offset = gameboard.offset_from_element(self.board.level_display, corner=(0, 1), offset=(0, 10))
        self.tiles = self.board.create_tiles(self.colors, offset=tile_offset)

        self.board.create_splash_menu(self.hi_scores)
        self.board.ui_elements = self.board.splash_elements

    def add_tile(self, tile):
        self.snake.add(tile)

    def animate(self):
        to_animate = [t for t in self.tiles if t.target != t.coords and not t.paused]
        for t in to_animate:
            t.ay += .4
            t.coords = (t.coords[0], min(t.coords[1] + t.ay, t.target[1]))
            if t.coords[1] == t.target[1]:
                t.ay = 0

        if self.animating and not to_animate:
            self.paused = False

        for tile in [t for t in self.tiles if t.attack_timer == 1]:
            tile.animate_beacon()

        d = self.board.level_display
        if d.progress > d.progress_actual:
            d.progress = 0
        if d.progress < d.progress_actual:
            amt = ceil((d.progress_actual - d.progress) / 8)
            d.progress += amt
        if d.progress >= d.progress_max:
            self.level_up()
            d.progress = 0
        d.update()

        h = self.board.hp_display
        amt = (h.hp - h.hp_displayed) / 20
        if h.fade_counter or not h.hp_displayed == h.hp:
            if abs(h.hp - h.hp_displayed) < .03:
                amt = h.hp - h.hp_displayed
            h.hp_displayed += amt
            h.update()
        if h.hp_displayed <= 0:
            if self.mode == 'play':
                self.game_over()

        for elem in [self.board.multiplier_display, self.board.longest_display, self.board.best_display]:
            if elem.fade_counter:
                elem.update()

    def apply_level_progress(self, exp):
        d = self.board.level_display
        d.progress_actual += exp
        d.update()

    def check_dictionary(self):
        return bool(self.snake.word.lower() in [x[0] for x in self.dictionary])

    def check_level_progress(self):
        return bool(self.board.level_display.progress >= self.board.level_display.progress_max)

    def check_update_best(self):
        if self.history[-1]['value'] > self.word_best['value']:
            self.level_best = self.level
            self.mult_best = self.multiplier
            text = f"{format(self.history[-1]['value'], ',d')} {self.history[-1]['word']}"
            filler = ['beige' for _ in range(len(text) - len(self.history[-1]['colors']))]
            obj = {
                'word': text,
                'value': self.history[-1]['value'],
                'colors': filler + self.history[-1]['colors']
            }
            self.word_best = obj
            self.board.best_display.set_colored_text(obj)
            self.board.best_display.flash()

    def check_update_longest(self):
        if self.word_longest:
            if len(self.history[-1]['word']) > len(self.word_longest):
                self.word_longest = self.history[-1]['word']
                self.board.longest_display.flash()
        else:
            self.word_longest = self.history[-1]['word']
            self.board.longest_display.flash()
        self.board.longest_display.set_text(self.word_longest)

    def choose_bonus_word(self):
        r_values = [0, 0, 0, 0.16, 0.22, 0.28, 0.36, 0.42, 0.48, 0.55, 0.61, 0.68, 0.74, 0.8, 0.87, 0.93, 0.99, 1.07, 1.13, 1.28, 1.31, 1.38]
        word_pool = [w[0] for w in self.dictionary if len(w[0]) == self.bonus_counter and w[1] > r_values[self.bonus_counter]]
        self.bonus_word = random.choice(word_pool).upper()

    def clear_marked(self):
        for tile in [t for t in self.tiles if t.marked]:
            tile.toggle_mark()

    def color_letters(self, word):
        for i, tile in enumerate(self.snake.tiles):
            if tile.tile_type == 'attack':
                word['colors'][i] = 'attack'
            elif tile.tile_type == 'heal':
                word['colors'][i] = 'teal'
            elif tile.tile_type == 'gold':
                word['colors'][i] = 'gold'
            elif tile.tile_type == 'poison':
                word['colors'][i] = 'poison'
            elif tile.tile_type == 'silver':
                word['colors'][i] = 'silver'

        return word

    def commit_word_to_history(self):
        if self.snake.word == self.bonus_word:
            color = 'green'
            value = 'M'
        else:
            color = 'beige'
            value = self.score_word()
        history_word = {
            'word': self.snake.word,
            'value': value,
            'colors': [color for _ in range(len(self.snake.word))]
        }
        history_word = self.color_letters(history_word)

        self.history.append(history_word)
        if len(self.history) > self.max_history_words:
            self.history.pop(0)
        self.last_five_words = [len(w['word']) for w in self.history[-5:]]

    def create_event_queue(self):
        queue = []

        for tile in self.snake.tiles:
            if tile.tile_type == 'heal':
                event = {
                    'tile': tile,
                    'event': 'heal',
                    'amount': tile.multiplier
                }
                queue.append(event)
        if self.snake.length:
            event = {
                'tiles': [t for t in self.snake.tiles if not t.tile_type == 'heal'],
                'event': 'submit',
                'amount': 0
            }
            queue.append(event)
        for tile in self.tiles:
            if tile.tile_type == 'poison':
                event = {
                    'tile': tile,
                    'event': 'poison',
                    'amount': tile.multiplier * -1
                }
                queue.append(event)
            elif tile.tile_type == 'attack':
                if tile.attack_timer > 1:
                    event = {
                        'tile': tile,
                        'event': 'tick',
                        'amount': 0
                    }
                else:
                    event = {
                        'tile': tile,
                        'event': 'attack',
                        'amount': tile.point_value * -1
                    }
                queue.append(event)
        return queue

    def empty_snake(self):
        print(f'empty_snake(): {len(self.snake.tiles)} tiles to empty')
        if not self.snake.tiles:
            return
        self.snake.last.mouse_out()
        for tile in [t for t in self.snake.tiles]:
            tile.beacon = False
            tile.highlighted = False
            tile.unselect()
        self.snake.tiles = []
        self.snake.update()

    def execute_event_queue(self, queue):
        # ---- DEBUG STUFF ----
        next_event = None
        following_events = []
        if queue:
            next_event = queue[0]
        if len(queue) > 1:
            following_events = queue[1:]
        if next_event:
            print(f'queue: [{next_event["event"]}]{", " if following_events else ""}{", ".join([e["event"] for e in following_events])}')
        # ---- DEBUG STUFF ----

        if not queue:
            if self.snake.length:
                self.reroll_tiles(self.snake.length)
                print('Queue empty; unpausing all tiles')
                for tile in [t for t in self.tiles if t.paused]:
                    tile.paused = False
                self.empty_snake()
                self.update_word_display()
            return
        event = queue[0]
        if event['event'] == 'submit':
            print(f'Removing {len(self.snake.tiles)} snake tiles')
            self.remove_tiles(self.snake.tiles, snake=True)
            queue.pop(0)
            threading.Timer(0.2, self.execute_event_queue, [queue]).start()
            return
        source_tile = event['tile']
        action = event['event']
        amt = event['amount']
        skip = False
        h = self.board.hp_display

        if action == 'heal':
            if h.hp == h.hp_max:
                h.hp_max += amt
                arc_sources = [source_tile.middle, 'teal', f'{self.multiplier} MAX', 'HP_MAX']
                self.board.gfx.create_ghost(source_tile, self.colors['teal'])
                self.board.gfx.draw_arcs([arc_sources])
                print(f'Heal effect from c{source_tile.col}r{source_tile.row} "{source_tile.letter}": HP_MAX increased by {self.multiplier}')
            else:
                h.hp = min(h.hp + amt, h.hp_max)
                arc_sources = [source_tile.middle, 'teal', amt, 'HP']
                self.board.gfx.draw_arcs([arc_sources])
                print(f'Healed {amt} from c{source_tile.col}r{source_tile.row} "{source_tile.letter}"')
            print(f'Removing heal tile "{source_tile.letter}" from snake.tiles')
            index = self.snake.tiles.index(source_tile)
            self.snake.tiles.pop(index)
            self.remove_tiles([source_tile])
            h.update()
        elif action == 'attack':
            # Don't activate tiles that are part of the just-submitted word
            if not source_tile in self.snake.tiles:
                source_tile.attack_tick()
                source_tile.update()
                h.hp += amt
                self.reroll_neighbor_tiles(source_tile)
                arc_sources = [source_tile.middle, 'bg_attack', amt, 'HP']
                self.board.gfx.draw_arcs([arc_sources])
                print(f'Dealt {amt * -1} damage from c{source_tile.col}r{source_tile.row} "{source_tile.letter}"')
            else:
                print('Attack tile removed via word submission')
        elif action == 'poison':
            # Don't activate tiles that are part of the just-submitted word
            if not source_tile in self.snake.tiles:
                # Ensure tile wasn't destroyed by a neighboring ATK tile
                if source_tile.tile_type == 'poison':
                    h.hp += amt
                    arc_sources = [source_tile.middle, 'poison_bright', amt, 'HP']
                    self.board.gfx.draw_arcs([arc_sources])
                    print(f'Poisoned {amt * -1} from c{source_tile.col}r{source_tile.row} "{source_tile.letter}"')
                else:
                    # Tile has already been destroyed
                    print(f'Queued tile c{source_tile.col}r{source_tile.row} "{source_tile.letter}" had a poison event, but was destroyed')
                    skip = True
            else:
                print('Poison tile removed via word submission')
        elif action == 'tick':
            # Don't activate tiles that are part of the just-submitted word
            if not source_tile in self.snake.tiles:
                if source_tile.tile_type == 'attack': # Ensure tile wasn't
                    source_tile.attack_tick()         # destroyed by a
                    source_tile.update()              # neighbor ATK tile
                    print(f'Attack tile c{source_tile.col}r{source_tile.row} "{source_tile.letter}" counted down to "{source_tile.attack_timer}"')
                else:
                    # Tile has already been destroyed
                    print(f'Queued tile c{source_tile.col}r{source_tile.row} "{source_tile.letter}" had a tick event, but was destroyed')
                    skip = True
            else:
                print('Attack tile had a tick event, but was removed via word submission')
        print(f'HP: {h.hp} / {h.hp_max}')

        if len(queue):
            self.paused = True
            queue.pop(0)
            if skip:
                self.execute_event_queue(queue)
            if not skip:
                threading.Timer(0.2, self.execute_event_queue, [queue]).start()
        else:
            self.paused = False
            for tile in [t for t in self.tiles if t.paused]:
                tile.paused = False

    def fetch_gamestates(self):
        with open('saved_gamestates.json') as file:
            gamestates = json.load(file)
        return gamestates

    def game_over(self):
        self.mode = 'menu'
        self.board.create_game_over_menu()
        self.board.ui_elements += self.board.splash_elements

    def get_attack_weight(self, avg):
        return -0.375 * avg + 1.975

    def handle_menu_btn_click(self, elem):
        if not isinstance(elem, Interactive):
            return
        if elem.name == 'quit':
            self.mode = 'menu'
            self.board.create_quit_menu()
            self.board.ui_elements += self.board.splash_elements
        elif elem.name == 'quit no':
            self.board.ui_elements = self.tiles + self.board.game_elements
            self.mode = 'play'
        elif elem.name == 'quit yes':
            self.try_update_hi_score_file()
            self.board.create_splash_menu(self.hi_scores)
            self.board.ui_elements = self.board.splash_elements
        elif elem.name == 'load':
            self.open_load_menu()
        elif elem.name == 'save':
            self.save_game()
        elif elem.name == 'scramble':
            if not self.paused:
                self.scramble()
                self.last_typed = ''
        elif elem.name == 'clear':
            if self.board.btn_clear_marked.enabled:
                self.clear_marked()
                self.board.btn_clear_marked.update()
                self.last_typed = ''
        elif elem.name == 'splash load':
            gamestates = self.fetch_gamestates()
            self.board.create_load_menu(gamestates)
            self.board.ui_elements = self.board.splash_elements
        elif elem.name == 'splash tutorial':
            self.board.create_tutorial()
            self.board.ui_elements = self.board.splash_elements
        elif elem.name == 'splash new':
            self.board.create_name_menu(self.player_name)
            self.board.ui_elements = self.board.splash_elements
            self.mode = 'name entry'
        elif elem.name == 'name start':
            if self.player_name:
                self.new_game()
                self.board.ui_elements = self.tiles + self.board.game_elements
                self.mode = 'play'
        elif elem.name == 'name clear':
            self.player_name = ''
            self.board.clear_name()
            self.board.ui_elements = self.board.splash_elements
        elif elem.name == 'tutorial next':
            self.board.advance_tutorial()
        elif elem.name == 'game over ok':
            self.try_update_hi_score_file()
            self.board.create_splash_menu(self.hi_scores)
            self.board.ui_elements = self.board.splash_elements
        elif elem.name in ('tutorial done', 'load back'):
            self.board.create_splash_menu(self.hi_scores)
            self.board.ui_elements = self.board.splash_elements
        elif 'gamestate' in elem.name:
            game_id = elem.name.split(' ')[-1]
            self.load_game(game_id)

    def handle_name_entry(self, key):
        letter = pygame.key.name(key).upper()
        if letter == 'RETURN':
            if self.player_name:
                self.new_game()
                self.board.ui_elements = self.tiles + self.board.game_elements
                self.mode = 'play'
        else:
            self.player_name = self.board.update_name(self.player_name, letter)
            self.board.ui_elements = self.board.splash_elements

    def highlight_selected_tiles(self):
        for tile in [t for t in self.tiles if t.selected]:
            tile.unselect()
        for tile in self.snake.tiles:
            tile.select()

    def highlight_tiles_from_letter(self, key, last_typed):
        letter = pygame.key.name(key).upper()
        if letter == 'Q':
            letter = 'Qu'

        # Type currently highlighted key or ESC to unhighlight all tiles
        if letter in (last_typed, 'ESCAPE'):
            self.unhighlight_all()
            self.last_typed = ''
        else:
            # Otherwise, highlight all tiles with matching letters
            for t in self.tiles:
                if t.letter == letter:
                    t.highlight()
                else:
                    t.unhighlight()
            self.last_typed = letter

    def level_up(self):
        d = self.board.level_display
        d.progress_actual -= d.progress_max
        d.progress_max += self.level * d.progress_lv_increment
        self.level += 1
        print(f'Level up: Lv{self.level}')
        d.flash()
        d.update(self.level)
        buff = self.board.hp_display.level_up(self.level)
        arc_sources = [[(125, 184), 'teal', str(buff), 'HP'], [(135, 180), 'teal', f'{buff} MAX', 'HP_MAX']]
        self.update_bonus_display()
        self.update_tiles()
        self.board.gfx.draw_arcs(arc_sources)

    def load_game(self, game_id):
        self.new_game()

        with open('saved_gamestates.json') as file:
            saved_gamestates = json.load(file)
        gamestate = [g for g in saved_gamestates if g['id'] == game_id][0]

        h = self.board.hp_display
        d = self.board.level_display

        d.progress_actual = gamestate['exp']
        d.progress_max = gamestate['next_level']
        h.hp = gamestate['hp']
        h.hp_max = gamestate['hp_max']
        self.bonus_counter = gamestate['bonus_counter']
        self.bonus_word = gamestate['bonus_word']
        self.history = gamestate['history']
        self.last_five_words = gamestate['last_five_words']
        self.level = gamestate['level']
        self.level_best = gamestate['level_best']
        self.score = gamestate['score']
        self.word_best = gamestate['best_word']
        self.word_longest = gamestate['longest_word']

        for n, tile in enumerate(self.tiles):
            source_tile = gamestate['tiles'][n]
            tile.attack_timer = source_tile['attack_timer']
            tile.col = source_tile['col']
            tile.first_turn = source_tile['first_turn']
            tile.letter = source_tile['letter']
            tile.marked = source_tile['marked']
            tile.multiplier = source_tile['multiplier']
            tile.point_value = source_tile['point_value']
            tile.row = source_tile['row']
            tile.tile_type = source_tile['tile_type']
            tile.update()

        self.board.best_display.set_colored_text(self.word_best)
        self.update_bonus_display()
        self.board.longest_display.update(self.word_longest)
        self.board.multiplier_display.update(self.multiplier)
        self.board.score_display.update(self.score)
        self.board.level_display.update(self.level)
        if self.history:
            self.board.history_display.set_multiline_text(self.history)

        self.board.ui_elements = self.tiles + self.board.game_elements
        self.mode = 'play'

    def load_hi_scores(self):
        with open('scores.json') as file:
            scores = json.load(file)
        return scores

    def mult_up(self):
        self.multiplier += 1
        self.bonus_counter += 1
        self.board.multiplier_display.flash()
        self.update_tiles()
        print(f'Multiplier set to {self.multiplier}')

    def new_game(self):
        self.animating = False
        self.bonus_counter = 3
        self.history = []
        self.last_five_words = []
        self.last_typed = ''
        self.level = 1
        self.level_best = 1
        self.mult_best = 1
        self.multiplier = 1
        self.paused = False
        self.prev_bonus = ''
        self.score = 0
        self.submitted_word = ''
        self.word_longest = None
        self.word_best = {
            "word": '',
            "value": 0,
            'colors': []
        }

        d = self.board.level_display
        d.progress = 0
        d.progress_actual = 0
        d.progress_max = d.progress_lv_increment

        h = self.board.hp_display
        h.hp_max = h.hp_max_base
        h.hp = h.hp_max
        h.hp_displayed = 1
        h.build_image()

        self.uncurrent_hi_scores()

        self.board.update_hi_score_display(self.hi_scores)
        self.choose_bonus_word()
        self.empty_snake()

        self.board.best_display.update(None)
        self.update_bonus_display()
        self.board.history_display.update(self.history)
        self.board.longest_display.update(self.word_longest)
        self.board.multiplier_display.update(self.multiplier)
        self.board.score_display.update(self.score)
        self.board.level_display.update(self.level, label=self.player_name)

        for t in self.tiles:
            t.reset()

    def open_load_menu(self):
        self.mode = 'menu'
        gamestates = self.fetch_gamestates()
        self.board.create_load_menu(gamestates)
        self.board.ui_elements = self.board.splash_elements

    def remove_tiles(self, tiles, snake=False):
        for tile in tiles:
            # Ghosts for neighbors of ATK tiles are handled in
            # reroll_neighbor_tiles()
            if snake:
                if self.submitted_word == self.prev_bonus:
                    self.board.gfx.create_ghost(tile, self.colors['bg_gold'])
                else:
                    if tile.tile_type == 'attack':
                        self.board.gfx.create_ghost(tile, self.colors['bg_attack'])
                    elif tile.tile_type == 'gold':
                        self.board.gfx.create_ghost(tile, self.colors['gold'])
                    elif tile.tile_type == 'poison':
                        self.board.gfx.create_ghost(tile, self.colors['poison'])
                    elif tile.tile_type == 'silver':
                        self.board.gfx.create_ghost(tile, self.colors['silver'])
                    else:
                        self.board.gfx.create_ghost(tile, self.colors['light_gray'])
            tile.reset()
            self.set_row(tile)
            # Push tiles with negative rows up off the top of the screen
            tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])
            tile.paused = True

    def reroll_neighbor_tiles(self, atk_tile):
        neighbors = [t for t in self.tiles if self.snake.is_neighbor(new_tile=t, old_tile=atk_tile)]
        neighbors.pop(neighbors.index(atk_tile))
        for tile in neighbors:
            self.board.gfx.create_ghost(tile, self.colors['red'])
            tile.reset()
            tile.paused = True
            self.set_row(tile)
            tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])
        atk_tile.row = min(atk_tile.row + 1, 6 + atk_tile.col % 2)
        self.update_tile_rows()

    def reroll_tiles(self, snake_length):
        self.update_tile_rows()
        tiles = [t for t in self.tiles if t.paused]
        print(f'reroll_tiles(): Rerolling {len(tiles)} tiles')
        tile_type = 'normal'
        special_index = 0

        if snake_length == 5:
            tile_type = 'heal'
        elif snake_length == 6:
            tile_type = 'silver'
        elif snake_length > 6:
            tile_type = 'gold'
        else:
            # Based on len of last 5 words
            # avg = 5; attack = 10%
            # avg = 3; attack = 85%
            if len(self.last_five_words) == 5:
                avg = round(sum(self.last_five_words) / len(self.last_five_words), 1)
                atk_weight = max(self.get_attack_weight(avg), 0)
                normal_weight = 1 - atk_weight
                atk_tile = choice([True, False], 1, p=[atk_weight, normal_weight])[0]
                if atk_tile:
                    tile_type = choice(['attack', 'poison'], 1, p=[0.8, 0.2])[0]
                else:
                    tile_type = 'normal'

        if tile_type != 'normal':
            # Randomly choose which new tile will have special type
            print(f'Special tile to be chosen from: {[t.letter for t in tiles]}')
            special_index = random.choice(range(len(tiles)))
            print(f'"{tiles[special_index].letter}" (i={special_index}) chosen for {tile_type} tile')
            tiles[special_index].tile_type = tile_type
            if tile_type == 'attack':
                self.set_attack_timer(tiles[special_index])
            tiles[special_index].update()
        else:
            print('No special tiles created for this batch')

    def save_game(self):
        h = self.board.hp_display
        d = self.board.level_display

        tiles = []
        for t in self.tiles:
            tile = {
                'attack_timer': t.attack_timer,
                'col': t.col,
                'first_turn': t.first_turn,
                'letter': t.letter,
                'marked': t.marked,
                'multiplier': t.multiplier,
                'point_value': t.point_value,
                'row': t.row,
                'tile_type': t.tile_type
            }
            tiles.append(tile)

        username = 'SHAT'
        stamp = datetime.today()
        timestamp_long =  datetime.strftime(stamp, '%b %d, %Y %H:%M:%S')
        timestamp_short =  datetime.strftime(stamp, '%Y-%m-%d-%H-%M-%S')

        gamestate = {
            'id': f'{username}_{timestamp_short}',
            'timestamp': timestamp_long,
            'username': username,
            'best_word': self.word_best,
            'bonus_counter': self.bonus_counter,
            'bonus_word': self.bonus_word,
            'exp': d.progress_actual,
            'history': self.history,
            'hp': h.hp,
            'hp_max': h.hp_max,
            'last_five_words': self.last_five_words,
            'level': self.level,
            'level_best': self.level_best,
            'longest_word': self.word_longest,
            'next_level': d.progress_max,
            'score': self.score,
            'tiles': tiles
        }

        with open('saved_gamestates.json') as file:
            saved_gamestates = [g for g in json.load(file)]

        saved_gamestates.append(gamestate)
        with open('saved_gamestates.json', 'w') as file:
            json.dump(saved_gamestates, file)

        print('Gamestate saved')

    def save_hi_scores(self, scores):
        with open('scores.json', 'w') as file:
            json.dump(scores, file)
        print('Hi scores updated')

    def score_word(self, word=None):
        value = 0
        if word:
            for l in word:
                value += self.board.lookup_letter_value(l) * self.multiplier * self.level
        else:
            for t in self.snake.tiles:
                value += t.point_value
            word = self.snake.word
        if word == self.bonus_word:
            value *= 3

        return value * len(word)

    def scramble(self, new_atk=True):
        print('----Scramble----')
        self.empty_snake()
        self.unhighlight_all()
        queue = self.create_event_queue()
        self.execute_event_queue(queue)

        if new_atk:
            try:
                atk = random.choice([t for t in self.tiles if (t.row == 0 and t.tile_type == 'normal')])
                atk.tile_type = 'attack'
                self.set_attack_timer(atk)
            except IndexError: # No normal tiles on top row
                pass
        for tile in [t for t in self.tiles if t.tile_type == 'normal']:
            tile.marked = False
            tile.choose_letter()

        self.update_tiles()

    def set_attack_timer(self, tile):
        if tile.tile_type == 'attack':
            letter_value = self.board.lookup_letter_value(tile.letter)
            if letter_value < 3:
                tile.attack_timer = 2
            elif letter_value < 8:
                tile.attack_timer = 3
            else:
                tile.attack_timer = 4
        else:
            tile.attack_timer = 4

    def set_row(self, tile):
        tile.row = min([t.row for t in self.tiles if t.col == tile.col]) - 1

    def toggle_mark(self, end_click_elem, start_click_elem):
        for elem in (start_click_elem, end_click_elem):
            if not elem:
                return
            if not isinstance(elem, Tile):
                return
        if end_click_elem == start_click_elem:
            elem.toggle_mark()
            self.unhighlight_all()

    def trim_snake(self, tile):
        index = len(self.snake.tiles) # Must use this instead of snake.length
                                      # due to 'Qu' tiles
        for t in reversed(self.snake.tiles):
            if t == tile:
                break
            index -= 1

        self.snake.tiles = self.snake.tiles[:index]
        self.snake.update()

    def try_add_tile(self, elem):
        if not isinstance(elem, Tile):
            return
        if elem in self.snake.tiles:
            self.trim_snake(elem)
        else:
            if self.snake.length:
                if self.snake.is_neighbor(elem):
                    self.add_tile(elem)
                else:
                    self.empty_snake()
                    self.add_tile(elem)
            else:
                self.add_tile(elem)

    def try_heal(self):
        h = self.board.hp_display
        return bool(h.hp < h.hp_max)

    def try_mouse_over(self, game_mode, elem):
        if game_mode in ('menu', 'name entry'):
            for el in [e for e in self.board.splash_elements if e.hovered]:
                el.mouse_out()
            if elem:
                elem.mouse_over()
        else:
            for el in [e for e in self.board.menu_btns + self.tiles if e.hovered]:
                el.mouse_out()
            if isinstance(elem, Interactive) or isinstance(elem, Tile):
                elem.mouse_over()

    def try_submit_word(self):
        self.paused = True
        if len(self.snake.tiles) == 1: # Must use this instead of
            self.empty_snake()         # snake.length due to 'Qu' tiles
            self.update_word_display()
            self.paused = False
        elif self.snake.length > 2:
            if self.check_dictionary():
                self.animating = True
                self.submitted_word = self.snake.word
                self.prev_bonus = self.bonus_word
                self.last_typed = ''
                self.unhighlight_all()
                self.commit_word_to_history()
                print(f'----Committed word "{self.snake.word}"----')
                self.check_update_longest()
                if self.snake.word == self.bonus_word:
                    print(f'Bonus word match')
                    self.mult_up()
                    self.update_mult_display()
                    self.choose_bonus_word()
                else:
                    score = self.score_word()
                    print(f'Added {score} to score')
                    self.score += score
                    self.update_score_display()
                    self.try_update_hi_scores()
                    self.check_update_best()
                    self.apply_level_progress(score)
                self.update_history_display()
                event_queue = self.create_event_queue()
                self.execute_event_queue(event_queue)
            else:
                print(f'Word "{self.snake.word}" not in dictionary')
                self.empty_snake()
                self.update_word_display()

    def try_update_hi_scores(self):
        scores = sorted(self.hi_scores, key=lambda k: k['score'])
        if self.score >= scores[0]['score']:
            scores.pop(0)
            entry = {
                'username': self.player_name,
                'score': self.score,
                'current': True
            }
            scores.append(entry)
            scores = sorted(scores,  key=lambda k: k['score'], reverse=True)
            self.board.update_hi_score_display(scores)

    def try_update_hi_score_file(self):
        scores = sorted(self.load_hi_scores(), key=lambda k: k['score'])
        if self.score >= scores[0]['score']:
            scores.pop(0)
            entry = {
                'username': self.player_name,
                'date': datetime.strftime(datetime.today(), '%b %d, %Y'),
                'score': self.score,
                'current': True
            }
            scores.append(entry)
            scores = sorted(scores,  key=lambda k: k['score'], reverse=True)
            self.save_hi_scores(scores)
            self.hi_scores = self.load_hi_scores()

    def uncurrent_hi_scores(self):
        for entry in self.hi_scores:
            entry['current'] = False
        self.save_hi_scores(self.hi_scores)

    def unhighlight_all(self):
        for t in self.tiles:
            t.unhighlight()

    def update_bonus_color(self):
        self.board.update_bonus_color(self.bonus_word, self.snake.word, self.colors)

    def update_bonus_display(self):
        if self.board.word_display.text:
            if self.board.word_display.text.split(' ')[0] == self.bonus_word:
                self.board.bonus_display.border_color = self.colors['green']
            else:
                self.board.bonus_display.border_color = self.colors['mid_gray']
        else:
            self.board.bonus_display.border_color = self.colors['mid_gray']

        self.board.bonus_display.set_text(self.bonus_word)

    def update_btn_clear_marked(self):
        self.board.btn_clear_marked.enabled = bool(len([t for t in self.tiles if t.marked]))
        self.board.btn_clear_marked.update()

    def update_history_display(self):
        self.board.history_display.set_multiline_text(self.history)

    def update_mult_display(self):
        self.board.multiplier_display.update(self.multiplier)

    def update_score_display(self):
        self.board.score_display.set_text(format(self.score, ',d'))

    def update_tile_rows(self):
        for col in range(7):
            col_tiles = [t for t in self.tiles if t.col == col]
            # Check if col needs rearranging
            if [x for x in col_tiles if x.row < 0]:
                col_tiles.sort(key=lambda t: t.row)
                for i in range(8):
                    try:
                        # Set row values back to 0-7
                        col_tiles[i].row = i
                        col_tiles[i].set_target(from_row_col=True)
                        col_tiles[i].set_middle()
                    except IndexError:
                        # Handle even (7 member) cols
                        pass

    def update_tiles(self):
        for t in self.tiles:
            t.update(level=self.level, multiplier=self.multiplier)

    def update_word_display(self):
        color = 'mid_gray'
        text = None
        value = 0
        word = self.snake.word

        if self.snake.length:
            if len(word) > 2:
                if self.check_dictionary():
                    if word == self.bonus_word:
                        color = 'green'
                        value = 'M'
                    else:
                        color = 'teal'
                        value = format(self.score_word(), ',d')
                else:
                    color = 'red'

            text = f"{word} (+{value})"

        self.board.word_display.border_color = self.colors[color]
        self.board.word_display.set_text(text)
