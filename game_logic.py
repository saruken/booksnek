import pygame, random

import gameboard, tile_snake

class Game:
    def __init__(self, dims, dictionary):
        self.colors = {
            'beige': pygame.Color('#aaaa66'),
            'bg_bomb': pygame.Color('#3b3245'),
            'bg_bomb_selected': pygame.Color('#655775'),
            'bg_crystal': pygame.Color('#349eeb'),
            'bg_crystal_selected': pygame.Color('#76bff5'),
            'bg_main': pygame.Color('#21282d'),
            'bg_back': pygame.Color('#38424d'),
            'bg_gold': pygame.Color('#ebc334'),
            'bg_gold_selected': pygame.Color('#fcde72'),
            'bg_normal': pygame.Color('#c1a663'),
            'bg_normal_selected': pygame.Color('#f0d081'),
            'bg_progress': pygame.Color('#161a1c'),
            'bg_silver': pygame.Color('#9eadad'),
            'bg_silver_selected': pygame.Color('#d5e7e8'),
            'bg_stone': pygame.Color('#5f666b'),
            'black': pygame.Color('#000000'),
            'border_gold': pygame.Color('#d4c413'),
            'dark_gray': pygame.Color('#202d36'),
            'light_gray': pygame.Color('#bfb9a8'),
            'mid_gray': pygame.Color('#546c7a'),
            'bomb': pygame.Color('#7c6e8a'),
            'gold': pygame.Color('#fce803'),
            'green': pygame.Color('#65a669'),
            'ocean': pygame.Color('#244254'),
            'progress': pygame.Color('#c9c618'),
            'red': pygame.Color('#e05a41'),
            'silver': pygame.Color('#d5e7e8'),
            'teal': pygame.Color('#50aef2')
        }

        self.board = gameboard.Board(dims=dims, coords=(0, 0), colors=self.colors)
        self.dictionary = dictionary
        self.snake = tile_snake.Snake()
        self.tiles = self.board.create_tiles(self.colors)
        self.ui_elements = self.tiles + self.board.ui_elements

        self.new_game()

    def add_tile(self, tile):
        self.snake.add(tile)
        self.set_current_word()

    def animate(self):
        to_animate = [t for t in self.tiles if t.target != t.coords]
        if not to_animate:
            return

        for t in to_animate:
            t.ay += .4
            t.coords = (t.coords[0], min(t.coords[1] + t.ay, t.target[1]))
            if t.coords[1] == t.target[1]:
                t.ay = 0

    def check_dictionary():
        return bool(self.current_word.lower() in self.dictionary)

    def check_level_progress(self):
        return bool(self.bonus_display.progress >= self.bonus_display.progress_max)

    def check_update_best():
        if self.history[-1]['value'] > self.value_best:
            self.level_best = self.level
            self.mult_best = self.multiplier
            self.value_best = self.history[-1]['value']
            self.word_best = self.history[-1]['word']
            text = f"{self.history[-1]['word']} (+{self.history[-1]['value']} / Lv {self.level_best} / x{self.mult_best})"
            filler = ['beige' for _ in range(len(text) - len(self.history[-1]['colors']))]
            obj = {
                'word': text,
                'colors': self.history[-1]['colors'] + filler
            }
            self.board.best_display.set_colored_text(obj)

    def check_update_longest():
        if len(self.history[-1]['word']) > len(self.word_longest):
            self.word_longest = self.history[-1]['word']
        self.board.longest_display.set_text(self.word_longest)

    def choose_bonus_word(self):
        word_pool = [w for w in self.dictionary if len(w) == self.bonus_counter]
        self.bonus_word = random.choice(word_pool).upper()

    def clear_marked(self):
        for tile in [t for t in self.tiles if t.marked]:
            tile.toggle_mark()

    def color_letters(word):
        for i, tile in enumerate(self.snake.tiles):
            if tile.tile_type == 'bomb':
                word['colors'][i] = 'bomb'
            elif tile.tile_type == 'crystal':
                word['colors'][i] = 'teal'
            elif tile.tile_type == 'gold':
                word['colors'][i] = 'gold'
            elif tile.tile_type == 'silver':
                word['colors'][i] = 'silver'

        return word

    def commit_word_to_history(self):
        if self.current_word == self.bonus_word:
            color = 'green'
            value = score_word(bonus=True)
        else:
            color = 'beige'
            value = score_word()
        history_word = {
            'word': self.current_word,
            'value': value,
            'colors': [color for _ in range(len(self.tiles))]
        }
        history_word = color_letters(history_word)

        self.history.append(history_word)
        self.last_five_words = self.history[-5:]

    def get_bomb_weight(self, avg):
        return -0.375 * avg + 1.975

    def empty_snake(self):
        self.snake.tiles = []
        self.snake.update()

    def highlight_selected_tiles():
        for tile in [t for t in self.tiles if t.selected]:
            tile.unselect()
        for tile in self.snake.tiles:
            tile.select()

    def new_game(self):
        self.bonus_counter = 3
        self.current_word = None
        self.history = []
        self.last_five_words = []
        self.last_typed = ''
        self.level = 1
        self.level_best = 1
        self.mult_best = 1
        self.multiplier = 1
        self.score = 0
        self.value_best = 0
        self.word_best = None
        self.word_longest = None

        self.choose_bonus_word()
        self.empty_snake()

        self.board.best_display.update(self.word_best)
        self.board.bonus_display.update(self.bonus_word)
        self.board.history_display.update(self.history)
        self.board.longest_display.update(self.word_longest)
        self.board.level_display.update(self.level)
        self.board.multiplier_display.update(self.multiplier)
        self.board.score_display.update(self.score)

        for t in self.tiles:
            t.reset()

        self.update_level_progress()

    def reroll_snake_tiles(self):
        for tile in self.snake.tiles:
            tile.choose_letter()
            tile.row = self.set_row(tile)
            # Push tiles with negative rows up off the top of the screen
            tile.set_coords(dy = tile.offset[1] * -1 - tile.dims[1])

        tile_type = 'normal'
        special_index = 0
        # Bomb tiles are created when your last 5 words have been on the
        # short side. Generally, maintaining an average of 5 letters
        # keeps you safe; anything below this and there's a better
        # chance of a bomb tile spawning.
        # avg = 5; bomb = 10%
        # avg = 3; bomb = 85%
        if len(last_five) == 5: #TODO: Fix this fn
            avg = round(sum(last_five) / len(last_five), 1)
            # Keep bomb_weight non-negative
            bomb_weight = self.get_bomb_weight(avg)
            normal_weight = 1 - bomb_weight
            tile_type = choice(['normal', 'bomb'], 1, p=[normal_weight, bomb_weight])[0]

        if self.snake.length == 5:
            tile_type = 'silver'
        elif self.snake.length == 6:
            tile_type = 'gold'
        elif self.snake.length > 6:
            tile_type = 'crystal'

        if tile_type != 'normal':
            # Randomly choose which new tile will have special type
            special_index = random.choice(range(len(self.tiles)))

        for i, tile in enumerate(self.snake.tiles):
            tile.marked = False
            tile.tile_type = tile_type if i == special_index else 'normal'
            tile.bomb_timer = 5
            tile.set_value(self.level, self.multiplier)

    def score_word(word=None):
        value = 0
        if word:
            for l in self.word:
                base_value += self.board.lookup_letter_value(l) * self.multiplier
        else:
            for t in self.snake.tiles:
                value += t.point_value
        if self.current_word == self.bonus_word:
            value *= 3

        value *= self.level
        return value * self.snake.length

    def scramble(self, new_bomb=True):
        if new_bomb:
            try:
                bomb = random.choice([t for t in self.tiles if (t.row == 0 and t.tile_type == 'normal')])
                bomb.tile_type = 'bomb'
                bomb.bomb_timer = 6
            except IndexError: # No normal tiles on top row
                pass
        for tile in self.tiles:
            if tile.tile_type == 'bomb':
                tile.bomb_timer -= 1
            elif tile.tile_type != 'stone':
                tile.marked = False
                tile.choose_letter()
                tile.tile_type = 'normal'
            tile.update(self.multiplier)

    def set_current_word(self):
        self.current_word = ''.join(self.snake.letters)

    def set_row(self, tile):
        '''
        Bumps tile rows "up" to a negative index while retaining their
        col values. If there is more than 1 tile to be moved up in a
        given column, stacks these tiles: row = -1, row = -2, etc.

        This fn only returns a row value; it has no bearing on actually
        drawing the tiles.
        '''

        index = self.tiles.index(tile)
        least_row = 0

        if index:
            prev_rows = [t.row for t in self.tiles[:index] if t.col == tile.col]
            if prev_rows:
                least_row = min(prev_rows)

        return least_row - 1

    def trim_snake(self, tile):
        index = len(self.snake.tiles)

        for t in reversed(self.snake.tiles):
            if t == tile:
                break
            index -= 1

        self.snake.tiles = self.snake.tiles[:index]

    def update_bonus_color(self):
        self.board.update_bonus_color(self.bonus_word, self.snake.word, self.colors)

    def update_bonus_display(self):
        self.board.bonus_display.set_text(f'{self.bonus_word} (+{str(self.score_word())})')

    def update_btn_clear_marked(self):
        self.board.btn_clear_marked.enabled = bool(len([t for t in self.tiles if t.marked]))
        self.board.btn_clear_marked.update()

    def update_history_display(self):
        self.board.history_display.set_colored_text(self.history)

    def update_level_progress(self):
        pass

    def update_score_display(self):
        self.board.score_display.set_text(str(self.score))

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
                    except IndexError:
                        # Handle even (7 member) cols
                        pass

    def update_word_display(self):
        color = 'dark_gray'
        text = ''
        value = 0
        word = self.snake.word

        if self.snake.length:
            if len(word) > 2:
                if self.check_dictionary(word):
                    value = score_word()
                    if word == self.bonus_word:
                        color = 'green'
                    else:
                        color = 'teal'
                else:
                    color = 'red'

            text = f"{word} (+{value})"

        word_display.set_border(color)
        word_display.set_text(text)
