import pygame, random
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
            'black': pygame.Color('#000000'),
            'border_gold': pygame.Color('#d4c413'),
            'dark_gray': pygame.Color('#202d36'),
            'hp_green': pygame.Color('#305431'),
            'hp_red': pygame.Color('#b3281e'),
            'hp_yellow': pygame.Color('#d16411'),
            'light_gray': pygame.Color('#bfb9a8'),
            'mid_gray': pygame.Color('#546c7a'),
            'poison': pygame.Color('#7c6e8a'),
            'gold': pygame.Color('#fce803'),
            'green': pygame.Color('#65a669'),
            'ocean': pygame.Color('#244254'),
            'progress': pygame.Color('#c9c618'),
            'red': pygame.Color('#e05a41'),
            'silver': pygame.Color('#d5e7e8'),
            'teal': pygame.Color('#50aef2'),
            'transparent': pygame.Color('#ff00ff')
        }

        self.board = gameboard.Board(dims=dims, coords=(0, 0), colors=self.colors)
        self.dictionary = dictionary
        self.snake = tile_snake.Snake()
        tile_offset = gameboard.offset_from_element(self.board.level_display, corner=(0, 1), offset=(0, 10))
        self.tiles = self.board.create_tiles(self.colors, offset=tile_offset)
        self.ui_elements = self.tiles + self.board.ui_elements

        self.new_game()

    def activate_tile_effects(self):
        arc_sources = []
        hp_effect = 0
        h = self.board.hp_display
        for tile in self.snake.tiles:
            if tile.tile_type == 'heal':
                arc_sources.append([tile.middle, 'teal'])
                amt = ceil(h.hp_max / 10)
                self.board.deltas.add(amt)
                hp_effect += amt
                print(f'Healed {amt} from c{tile.col}r{tile.row} "{tile.letter}"')

        self.reroll_snake_tiles()

        for tile in [t for t in self.tiles if t.tile_type == 'attack']:
            if tile.attack_tick():
                arc_sources.append([tile.middle, 'bg_attack'])
                amt = ceil(self.board.hp_display.hp_max / 8) * -1
                hp_effect += amt
                print(f'Damaged {amt} from c{tile.col}r{tile.row} "{tile.letter}"')
                self.board.deltas.add(amt)
                self.reroll_tiles(tile=tile)

        for tile in [t for t in self.tiles if t.tile_type == 'poison']:
            if tile.first_turn:         # Prevent poison tiles from dealing
                tile.first_turn = False # damage the turn they come into play
            else:
                arc_sources.append([tile.middle, 'bg_poison'])
                amt = ceil(h.hp_max / 16) * -1
                hp_effect += amt
                print(f'Poisoned {amt} from c{tile.col}r{tile.row} "{tile.letter}"')
                self.board.deltas.add(amt)

        self.update_tile_rows()

        if hp_effect > 0:
            h.flash(color='green')
        elif hp_effect < 0:
            h.flash(color='red')
        new_hp = h.hp + hp_effect
        h.hp = max(0, min(new_hp, h.hp_max))

        if arc_sources:
            self.board.gfx.draw_arcs(arc_sources) # Move up before reroll

    def add_tile(self, tile):
        self.snake.add(tile)

    def animate(self):
        to_animate = [t for t in self.tiles if t.target != t.coords]
        for t in to_animate:
            t.ay += .4
            t.coords = (t.coords[0], min(t.coords[1] + t.ay, t.target[1]))
            if t.coords[1] == t.target[1]:
                t.ay = 0
        if not to_animate:
            self.paused = False

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
            self.game_over()

        for elem in [self.board.multiplier_display, self.board.longest_display, self.board.best_display]:
            if elem.fade_counter:
                elem.update()

    def apply_level_progress(self, exp):
        d = self.board.level_display
        d.progress_actual += exp
        d.update()

    def check_dictionary(self):
        return bool(self.snake.word.lower() in self.dictionary)

    def check_level_progress(self):
        return bool(self.board.level_display.progress >= self.board.level_display.progress_max)

    def check_update_best(self):
        if self.history[-1]['value'] > self.value_best:
            self.level_best = self.level
            self.mult_best = self.multiplier
            self.value_best = self.history[-1]['value']
            self.word_best = self.history[-1]['word']
            text = f"{format(self.history[-1]['value'], ',d')} {self.history[-1]['word']}"
            filler = ['beige' for _ in range(len(text) - len(self.history[-1]['colors']))]
            obj = {
                'word': text,
                'colors': filler + self.history[-1]['colors']
            }
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
        word_pool = [w for w in self.dictionary if len(w) == self.bonus_counter]
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
        self.last_five_words = [len(w['word']) for w in self.history[-5:]]

    def empty_snake(self):
        for tile in [t for t in self.snake.tiles]:
            tile.unselect()
        self.snake.tiles = []
        self.snake.update()

    def game_over(self):
        print('game_over() placeholder')

    def get_enemy_weight(self, avg):
        return -0.375 * avg + 1.975

    def handle_menu_btn_click(self, elem):
        if not isinstance(elem, Interactive):
            return
        if elem.name == 'new':
            self.new_game()
        elif elem.name == 'open':
            self.load_game()
        elif elem.name == 'save':
            if self.board.menu_save.enabled:
                self.save_game()
        elif elem.name == 'scramble':
            self.scramble()
            self.last_typed = ''
        elif elem.name == 'clear':
            if self.board.btn_clear_marked.enabled:
                self.clear_marked()
                self.board.btn_clear_marked.update()
                self.last_typed = ''

    def heal(self, tile):
        h = self.board.hp_display
        amt = ceil(h.hp_max / 10)
        self.board.deltas.add(amt)
        h.hp = min(h.hp + amt, h.hp_max)
        h.flash(color='green')
        # TODO: Create arc from tile to HP display

    def highlight_selected_tiles(self):
        for tile in [t for t in self.tiles if t.selected]:
            tile.unselect()
        for tile in self.snake.tiles:
            tile.select()

    def highlight_tiles_from_letter(self, key, last_typed):
        letter = pygame.key.name(key).upper()
        if letter == 'Q':
            letter = 'Qu'

        # Type currently highlighted key to unhighlight all tiles
        if letter in (last_typed, 'ESCAPE'):
            for t in self.tiles:
                t.mouse_out()
            return ''
        else:
            # Otherwise, highlight all tiles with matching letters
            for t in self.tiles:
                if t.letter == letter:
                    t.mouse_over()
                else:
                    t.mouse_out()
        # Return typed key to store as last_typed
        return letter

    def level_up(self):
        d = self.board.level_display
        d.progress_actual -= d.progress_max
        d.progress_max += self.level * d.progress_lv_increment
        self.level += 1
        d.flash()
        d.update(self.level)
        self.board.hp_display.level_up(self.level)
        self.update_bonus_display()
        self.update_tiles()

    def load_game(self):
        h = self.board.hp_display
        print(f'hp: {h.hp}; hp_displayed: {h.hp_displayed}; hp_max: {h.hp_max}')

    def mult_up(self):
        self.multiplier += 1
        self.bonus_counter += 1
        self.board.multiplier_display.flash()

    def new_game(self):
        self.bonus_counter = 3
        self.history = []
        self.last_five_words = []
        self.last_typed = ''
        self.level = 1
        self.level_best = 1
        self.mult_best = 1
        self.multiplier = 1
        self.paused = False
        self.score = 0
        self.value_best = 0
        self.word_best = None
        self.word_longest = None

        self.choose_bonus_word()
        self.empty_snake()

        self.board.best_display.update(self.word_best)
        self.update_bonus_display()
        self.board.history_display.update(self.history)
        self.board.longest_display.update(self.word_longest)
        self.board.multiplier_display.update(self.multiplier)
        self.board.score_display.update(self.score)
        self.board.level_display.update(self.level)

        for t in self.tiles:
            t.reset()

    def reroll_snake_tiles(self):
        for tile in self.snake.tiles:
            self.board.gfx.create_ghost(tile, self.colors['light_gray'])
            tile.choose_letter()
            self.set_row(tile)
            # Push tiles with negative rows up off the top of the screen
            tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])

        tile_type = 'normal'
        special_index = 0

        if self.snake.length == 5:
            tile_type = 'heal'
        elif self.snake.length == 6:
            tile_type = 'silver'
        elif self.snake.length > 6:
            tile_type = 'gold'
        else:
        # Based on len of last 5 words
        # avg = 5; attack = 10%
        # avg = 3; attack = 85%
            if len(self.last_five_words) == 5:
                avg = round(sum(self.last_five_words) / len(self.last_five_words), 1)
                enemy_weight = max(self.get_enemy_weight(avg), 0)
                normal_weight = 1 - enemy_weight
                enemy_tile = choice([True, False], 1, p=[enemy_weight, normal_weight])[0]
                if enemy_tile:
                    tile_type = choice(['attack', 'poison'], 1, p=[0.8, 0.2])[0]
                else:
                    tile_type = 'normal'

        if tile_type != 'normal':
            # Randomly choose which new tile will have special type
            special_index = random.choice(range(len(self.snake.tiles)))

        for i, tile in enumerate(self.snake.tiles):
            tile.marked = False
            tile.tile_type = tile_type if i == special_index else 'normal'
            tile.attack_timer = 5
            tile.first_turn = True

    def reroll_tiles(self, tile):
        neighbors = [t for t in self.tiles if self.snake.is_neighbor(new_tile=t, old_tile=tile)]
        neighbors.pop(neighbors.index(tile))
        for tile in neighbors:
            tile.reset()
            self.set_row(tile)
            tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])
        tile.row = min(tile.row + 1, 6 + tile.col % 2)
        self.update_tile_rows()

    def save_game(self):
        print('save_game() placeholder')

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
        self.empty_snake()
        self.activate_tile_effects()

        if new_atk:
            try:
                atk = random.choice([t for t in self.tiles if (t.row == 0 and t.tile_type == 'normal')])
                atk.tile_type = 'attack'
                atk.attack_timer = 5
            except IndexError: # No normal tiles on top row
                pass
        for tile in [t for t in self.tiles if t.tile_type not in ('attack', 'poison', 'stone')]:
            tile.marked = False
            tile.choose_letter()
            tile.tile_type = 'normal'

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
        for tile in [t for t in self.snake.tiles if t.tile_type == 'heal']:
            self.heal(tile)

    def try_mouse_over(self, elem):
        for el in [e for e in self.board.menu_btns + self.tiles if e.hovered]:
            el.mouse_out()
        if isinstance(elem, Interactive) or isinstance(elem, Tile):
            elem.mouse_over()

    def try_submit_word(self):
        if len(self.snake.tiles) == 1: # Must use this instead of
            self.empty_snake()         # snake.length due to 'Qu' tiles
        elif self.snake.length > 2:
            if self.check_dictionary():
                print(f'Committed word "{self.snake.word}"')
                self.paused = True
                self.last_typed = ''
                self.commit_word_to_history()
                self.check_update_longest()
                if self.snake.word == self.bonus_word:
                    print(f'This is the bonus word')
                    self.mult_up()
                    self.update_mult_display()
                    self.choose_bonus_word()
                else:
                    score = self.score_word()
                    print(f'Added {score} to score')
                    self.score += score
                    self.update_score_display()
                    self.check_update_best()
                    self.apply_level_progress(score)
                self.update_history_display()
                self.activate_tile_effects()
            else:
                print(f'Word "{self.snake.word}" not in dictionary')

            self.snake.last.mouse_out()
            self.empty_snake()
            self.update_word_display()

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
