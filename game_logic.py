import json, pygame, random, threading
from datetime import datetime
from math import ceil, floor

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
        self.queue = []
        self.snake = tile_snake.Snake()
        tile_offset = gameboard.offset_from_element(self.board.level_display, corner=(0, 1), offset=(0, 10))
        self.tiles = self.board.create_tiles(self.colors, offset=tile_offset)

        self.board.create_splash_menu(self.hi_scores)
        self.board.ui_elements = self.board.splash_elements

    def add_gold_tile_event(self, tile, turn_index=1, traversed=None):
        if not traversed:  # Have to use this workaround due to behavior
            traversed = [] # of mutable defaults in Python
        traversed.append(tile.identify())
        if tile.tile_type == 'heal':
            print(f'Creating heal event @ {tile.identify()} from gold tile neighbor')
            event = {
                'tile': tile,
                'event': 'heal',
                'amount': tile.multiplier,
                'turn': turn_index
            }
            return event
        elif tile.tile_type == 'gold':
            print(f'Creating gold tile event @ {tile.identify()}')
            turn_index += 1
            event = {
                'tile': tile,
                'event': 'explode',
                'turn': turn_index
            }
            for t in self.get_neighbors(tile):
                if not t.identify() in traversed:
                    self.queue.append(self.add_gold_tile_event(t, turn_index, traversed))
            return event
        else:
            print(f'Creating explode tile event @ {tile.identify()} from gold tile neighbor')
            event = {
                'tile': tile,
                'event': 'explode',
                'turn': turn_index
            }
            return event

    def add_tile(self, tile):
        self.snake.add(tile)

    def animate(self):
        to_animate = [t for t in self.tiles if t.target != t.coords and not t.paused]
        if to_animate:
            self.animating = True
        for t in to_animate:
            t.ay += .4
            t.coords = (t.coords[0], min(t.coords[1] + t.ay, t.target[1]))
            if t.coords[1] == t.target[1]:
                t.ay = 0

        if self.animating and not to_animate:
            self.input_disabled = False

        for tile in [t for t in self.tiles if t.event_timer == 1 and t.tile_type == 'attack']:
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

    def check_update_longest(self, word):
        if self.word_longest:
            if len(word) > len(self.word_longest):
                self.word_longest = word
        else:
            self.word_longest = word
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

    def commit_word_to_history(self, word):
        print(f'----Committed word "{word}"----')
        color = 'green' if word == self.bonus_word else 'beige'
        history_word = {
            'word': word,
            'value': self.score_word(word),
            'colors': [color for _ in range(len(word))]
        }
        history_word = self.color_letters(history_word)

        self.history.append(history_word)
        if len(self.history) > self.max_history_words:
            self.history.pop(0)
        self.last_five_words = [len(w['word']) for w in self.history[-5:]]

    def create_event_queue(self, ghost_color=None):
        print('Creating event queue...')
        self.queue = []
        event_tiles = []
        for tile in self.snake.tiles:
            if tile.tile_type == 'heal':
                print(f'Creating heal event from snake tile: {tile.identify()}')
                event = {
                    'tile': tile,
                    'event': 'heal',
                    'amount': tile.multiplier,
                    'turn': 0
                }
                self.queue.append(event)
            elif tile.tile_type == 'gold':
                self.queue.append(self.add_gold_tile_event(tile))
            else:
                print(f'Creating remove event from snake tile: {tile.identify()}')
                event = {
                    'tile': tile,
                    'event': 'remove',
                    'ghost_color': ghost_color,
                    'turn': 1
                }
                self.queue.append(event)
        turn = 2
        for tile in [t for t in self.tiles if t.tile_type == 'poison']:
            print(f'Creating poison event from board tile: {tile.identify()}')
            event = {
                'tile': tile,
                'event': 'poison',
                'amount': tile.multiplier * -1,
                'turn': turn
            }
            self.queue.append(event)
            turn += 1
        for tile in [t for t in self.tiles if t.tile_type == 'attack' and t.event_timer == 1 and t not in self.snake.tiles]:
            print(f'Creating attack event from board tile: {tile.identify()}')
            event = {
                'tile': tile,
                'event': 'attack',
                'amount': tile.point_value * -1,
                'turn': turn
            }
            self.queue.append(event)
            for t in self.get_neighbors(tile):
                print(f'Creating remove event from attack tile neighbor: {tile.identify()}')
                event = {
                    'tile': t,
                    'event': 'kill',
                    'turn': turn
                }
                self.queue.append(event)
        for tile in [t for t in self.tiles if t.tile_type == 'attack' and t.event_timer > 1]:
            print(f'Creating tick event from board tile: {tile.identify()}')
            event = {
                'tile': tile,
                'event': 'tick',
                'turn': turn
            }
            self.queue.append(event)
            turn += 1
        event_tiles = list(set([e['tile'] for e in self.queue]))
        print(f'Queue contains {len(self.queue)} event(s) for {len(event_tiles)} unique tile(s)')
        if self.queue:
            print(f'    Unique tile(s) in event queue: {", ".join([t.identify() for t in event_tiles])}')
        # Drop potential null events from gold tiles
        self.queue = [e for e in self.queue if e]
        print('Sorting event queue by turn')
        self.queue = sorted(self.queue, key=lambda k: k['turn'])
        for i in range(len(self.queue)):
            event = self.queue[i]
            print(f'Reviewing {event["event"]} event for {event["tile"].identify()}')
            if event['tile'] not in event_tiles:
                print(f'    {event["tile"].identify()} already in event queue for another event; discarding {event["event"]} event')
                self.queue[i] = None
            else:
                event_tiles.pop(event_tiles.index(event['tile']))
                print(f'    Adding {event["event"]} event for {event["tile"].identify()} to event queue')
        # Drop potential null events from repeated tiles
        self.queue = [e for e in self.queue if e]
        if self.queue:
            self.group_queue_by_turns()
        print('Event queue complete')

    def create_tile_from_last_5(self):
        # Based on len of last 5 words
        # avg = 5; attack = 10%
        # avg = 3; attack = 85%
        if len(self.last_five_words) == 5:
            avg = round(sum(self.last_five_words) / len(self.last_five_words), 1)
            atk_weight = max(self.get_attack_weight(avg), 0)
            normal_weight = 1 - atk_weight
            special = random.choices(population=[True, False], weights=[atk_weight, normal_weight], k=1)[0]
            if special:
                tile_type = random.choices(population=['attack', 'poison'], weights=[0.8, 0.2], k=1)[0]
            else:
                tile_type = 'normal'
        else:
            tile_type = 'normal'
        return tile_type

    def execute_event_queue(self):
        # ---- DEBUG STUFF ----
        if self.queue:
            current_turn = self.queue[0][0]['turn']
            print(f'Current turn: {current_turn}')
            print(f'Remaining turns: {len(self.queue) - 1}')
            print('Things happening this turn:')
            print('    ' + '; '.join([e['event'] + ' ' + e['tile'].identify() for e in self.queue[0]]))
        # ---- DEBUG STUFF ----

        if not self.queue:
            if self.snake.length:
                self.update_tile_rows()
                self.roll_create_special_tile(self.snake.length)
                self.snake.empty()
                self.update_word_display()
            else:
                self.animating = True
            print('Queue empty; unpausing all tiles')
            for tile in [t for t in self.tiles if t.paused]:
                tile.paused = False
            return
        for event in self.queue.pop(0):
            tile = event['tile']
            action = event['event']
            if action == 'remove':
                if tile.tile_type == 'attack':
                    color = 'red'
                elif tile.tile_type == 'poison':
                    color = 'poison'
                elif tile.tile_type == 'silver':
                    color = 'silver'
                else:
                    try:
                        color = event['ghost_color'] # Special bonus word color
                    except AttributeError:
                        color = 'beige'
                self.board.gfx.create_ghost(tile, self.colors[color])
                print(f'Removing tile @ c{tile.col}r{tile.row} "{tile.letter}"')
                self.remove_tile(tile)
            elif action == 'heal':
                h = self.board.hp_display
                if h.hp == h.hp_max:
                    h.hp_max += event['amount']
                    arc_sources = [tile.middle, 'teal', f'{self.multiplier} MAX', 'HP_MAX', 0]
                    self.board.gfx.create_ghost(tile, self.colors['teal'])
                    self.board.gfx.draw_arcs([arc_sources])
                    print(f'Heal effect from {tile.identify()}: HP_MAX increased by {self.multiplier}')
                else:
                    h.hp = min(h.hp + event['amount'], h.hp_max)
                    arc_sources = [tile.middle, 'teal', event['amount'], 'HP', 20]
                    self.board.gfx.draw_arcs([arc_sources])
                    print(f'Healed {event["amount"]} from {tile.identify()}')
                self.board.gfx.create_ghost(tile, self.colors['teal'])
                self.remove_tile(tile)
                h.update()
            elif action == 'explode':
                self.board.gfx.create_ghost(tile, self.colors['gold'])
                print(f'{tile.identify()} blew up')
                self.remove_tile(tile)
            elif action == 'kill':
                self.board.gfx.create_ghost(tile, self.colors['red'])
                print(f'{tile.identify()} was blown up by an attack tile')
                self.remove_tile(tile)
            elif action == 'attack':
                # Don't activate tiles that are part of the just-submitted word
                if not tile in self.snake.tiles:
                    tile.attack_tick()
                    tile.update()
                    h = self.board.hp_display
                    h.hp += event['amount']
                    arc_sources = [tile.middle, 'bg_attack', event['amount'], 'HP', -20]
                    self.board.gfx.create_ghost(tile, self.colors['red'])
                    print(f'Dealt {event["amount"] * -1} damage from {tile.identify()}')
                    self.board.gfx.draw_arcs([arc_sources])
                    self.remove_tile(tile)
                else:
                    print('Attack tile removed via word submission')
            elif action == 'poison':
                # Don't activate tiles that are part of the just-submitted word
                if not tile in self.snake.tiles:
                    # Ensure tile wasn't destroyed by a neighboring ATK tile
                    if tile.tile_type == 'poison':
                        tile.poison_tick()
                        tile.update()
                        h = self.board.hp_display
                        h.hp += event['amount']
                        arc_sources = [tile.middle, 'poison_bright', event['amount'], 'HP', -20]
                        self.board.gfx.draw_arcs([arc_sources])
                        print(f'Poisoned {event["amount"] * -1} from {tile.identify()}')
                    else:
                        # Tile has already been destroyed
                        print(f'Queued tile {tile.identify()} had a poison event, but was destroyed')
                else:
                    print('Poison tile removed via word submission')
            elif action == 'tick':
                # Don't activate tiles that are part of the just-submitted word
                if not tile in self.snake.tiles:
                    if tile.tile_type == 'attack': # Ensure tile wasn't
                        tile.attack_tick()         # destroyed by a
                        tile.update()              # neighbor ATK tile
                        print(f'Attack tile {tile.identify()} counted down to "{tile.event_timer}"')
                    else:
                        # Tile has already been destroyed
                        print(f'Queued tile {tile.identify()} had a tick event, but was destroyed')
                else:
                    print('Attack tile had a tick event, but was removed via word submission')
            h = self.board.hp_display
            print(f'HP: {h.hp} / {h.hp_max}')
        threading.Timer(0.2, self.execute_event_queue).start()

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

    def get_neighbors(self, base_tile):
        neighbors = [t for t in self.tiles if self.board.is_neighbor(new_tile=t, old_tile=base_tile) and not t == base_tile]
        print(f'get_neighbors(): Neighbors of {base_tile.tile_type} tile {base_tile.identify()} are: {", ".join([t.identify() for t in neighbors])}')
        return neighbors

    def group_queue_by_turns(self):
        print('Grouping queue events by turn')
        queue = [[] for _ in range(max([e['turn'] for e in self.queue]) + 1)]
        for event in self.queue:
            queue[event['turn']].append(event)
        self.queue = [e for e in queue if e] # Ditch empty turns
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
            if not self.input_disabled:
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
        elif elem.name == 'invalid word ok':
            self.board.ui_elements = self.tiles + self.board.game_elements
            self.mode = 'play'
        elif elem.name == 'game saved ok':
            self.mode = 'play'
            self.board.ui_elements = self.tiles + self.board.game_elements
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
        arc_sources = [[(125, 184), 'bg_gold', str(buff), 'HP', 0], [(135, 180), 'bg_gold', f'{buff} MAX', 'HP_MAX', 0]]
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
            tile = gamestate['tiles'][n]
            tile.event_timer = tile['attack_timer']
            tile.col = tile['col']
            tile.first_turn = tile['first_turn']
            tile.letter = tile['letter']
            tile.marked = tile['marked']
            tile.multiplier = tile['multiplier']
            tile.point_value = tile['point_value']
            tile.row = tile['row']
            tile.tile_type = tile['tile_type']
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
        self.input_disabled = False
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
        self.snake.empty()

        self.board.best_display.update(None)
        self.update_bonus_display()
        self.board.history_display.update(self.history)
        self.board.longest_display.update(self.word_longest)
        self.board.multiplier_display.update(self.multiplier)
        self.board.score_display.update(self.score)
        self.board.level_display.update(self.level, label=f'LEVEL: {self.player_name}')

        for t in self.tiles:
            t.reset()

    def open_load_menu(self):
        self.mode = 'menu'
        gamestates = self.fetch_gamestates()
        self.board.create_load_menu(gamestates)
        self.board.ui_elements = self.board.splash_elements

    def remove_tile(self, tile):
        tile.reset()
        self.set_row(tile)
        # Push tiles with negative rows up off the top of the screen
        tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])
        tile.paused = True

    def roll_create_special_tile(self, snake_length):
        '''
        Creates spcial tiles based on:
            1. The number of tiles in player's last word, or
            2. The average number of tiles in player's last 5 words

        If player submits a valid word of length 5+, a special (silver,
        heal or gold) tile will always be created. If player submits a
        valid word of length < 5, a negative special (attack, poison)
        tile may be created; the odds of this are determined by a
        rolling average of player's last 5 word lengths.
        '''
        tiles = [t for t in self.tiles if t.paused]
        print(f'roll_create_special_tile(): Rerolling {len(tiles)} tiles')
        tile_type = 'normal'
        special_index = 0

        if snake_length == 5:
            tile_type = 'silver'
        elif snake_length == 6:
            tile_type = 'heal'
        elif snake_length > 6:
            tile_type = 'gold'
        else:
            tile_type = self.create_tile_from_last_5()

        if tile_type != 'normal':
            # Randomly choose which new tile will have the special type
            special_index = random.choice(range(len(tiles)))
            print(f'"{tiles[special_index].letter}" (i={special_index}) chosen for {tile_type} tile')
            tiles[special_index].tile_type = tile_type
            if tile_type == 'attack':
                self.set_tile_timer(tiles[special_index])
            else:
                tiles[special_index].event_timer = 3
            tiles[special_index].update()
        else:
            print('No special tiles created for this batch')

    def save_game(self):
        h = self.board.hp_display
        d = self.board.level_display

        tiles = []
        for t in self.tiles:
            tile = {
                'attack_timer': t.event_timer,
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

        stamp = datetime.today()
        timestamp_long =  datetime.strftime(stamp, '%b %d, %Y %H:%M:%S')
        timestamp_short =  datetime.strftime(stamp, '%Y-%m-%d-%H-%M-%S')

        gamestate = {
            'id': f'{self.player_name}_{timestamp_short}',
            'timestamp': timestamp_long,
            'username': self.player_name,
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

        self.mode = 'menu'
        self.board.create_game_saved_menu(gamestate['id'])
        self.board.ui_elements += self.board.splash_elements
        print('Gamestate saved')

    def save_hi_scores(self, scores):
        with open('scores.json', 'w') as file:
            json.dump(scores, file)
        print('Hi scores updated')

    def score_word(self, word):
        value = 0
        for l in word:
            value += self.board.lookup_letter_value(l) * self.multiplier
        return value * len(word)

    def scramble(self):
        print('----Scramble----')
        self.snake.empty()
        self.unhighlight_all()
        self.create_event_queue()
        self.execute_event_queue()

        try:
            atk = random.choice([t for t in self.tiles if (t.row == 0 and t.tile_type == 'normal')])
            atk.tile_type = 'attack'
            self.set_tile_timer(atk)
            atk.update()
        except IndexError:
            print('scramble(): No "normal" type tiles on top row')
            pass
        for tile in [t for t in self.tiles if t.tile_type == 'normal']:
            tile.marked = False
            tile.choose_letter()

        self.update_tiles()

    def set_tile_timer(self, tile):
        if tile.tile_type == 'attack':
            letter_value = self.board.lookup_letter_value(tile.letter)
            if letter_value < 3:
                tile.event_timer = 2
            elif letter_value < 8:
                tile.event_timer = 3
            else:
                tile.event_timer = 4
        else:
            tile.event_timer = 5 # Default for poison tiles

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
                if self.board.is_neighbor(new_tile=elem, old_tile=self.snake.last):
                    self.add_tile(elem)
                else:
                    self.snake.empty()
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
        if len(self.snake.tiles) == 1: # Must use this instead of
            self.snake.empty()         # snake.length due to 'Qu' tiles
        elif self.snake.length > 2:
            if self.check_dictionary():
                self.input_disabled = True
                multUP_flag = True if self.snake.word == self.bonus_word else False
                word = self.snake.word
                self.prev_bonus = self.bonus_word
                self.last_typed = ''
                self.commit_word_to_history(word)
                self.check_update_longest(word)
                score = self.score_word(word)
                self.score += score
                self.update_score_display()
                self.try_update_hi_scores()
                self.check_update_best()
                self.apply_level_progress(score)
                self.update_history_display()
                ghost_color = 'beige'
                if multUP_flag:
                    self.mult_up()
                    self.update_mult_display()
                    self.choose_bonus_word()
                    ghost_color = 'gold'
                self.create_event_queue(ghost_color)
                self.execute_event_queue()
            else:
                print(f'Word "{self.snake.word}" not in dictionary')
                self.mode = 'menu'
                self.board.create_invalid_word_menu(self.snake.word)
                self.board.ui_elements += self.board.splash_elements
                self.snake.empty()
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
        for tile in [t for t in self.tiles if t.tile_type == 'normal']:
            tile.update(multiplier=self.multiplier)

    def update_word_display(self):
        color = 'mid_gray'
        text = None
        value = 0
        word = self.snake.word

        if self.snake.length:
            if len(word) > 2:
                if self.check_dictionary():
                    value = format(self.score_word(word), ',d')
                    if word == self.bonus_word:
                        color = 'green'
                    else:
                        color = 'teal'
                else:
                    color = 'red'

            text = f"{word} (+{value})"

        self.board.word_display.border_color = self.colors[color]
        self.board.word_display.set_text(text)
