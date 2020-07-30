# Common modules
import pygame
from math import floor
# Hot, single imports in your local directory
import gameboard, tile_snake, ui_btn, ui_display

def check_dictionary(word):

    global DICTIONARY

    return bool(word.lower() in DICTIONARY)

def check_best(best, new_word):

    if best:
        if new_word['value'] > best['value']:
            return new_word
        return best
    else:
        return new_word

def check_longest(longest, new_word):

    if longest:
        if len(new_word['word']) > len(longest):
            return new_word['word']
        return longest
    else:
        return new_word['word']

def color_letters(tiles, history_entry):

    for i in range(len(tiles)):
        if tiles[i].tile_type == 'bomb':
            history_entry['colors'][i] = 'bomb'
        elif tiles[i].tile_type == 'gold':
            history_entry['colors'][i] = 'gold'
        elif tiles[i].tile_type == 'crystal':
            history_entry['colors'][i] = 'teal'

    return history_entry

def do_clear():

    pass

def do_mark():

    pass

def do_scramble(snake, board):

    snake.new()
    board.scramble()

def is_neighbor(new_tile, old_tile):

    # There are 4 'false' neighbors, depending on which col old_tile is in:
        # Even old_tile.cols:
            # new_c == old_c + 1 and new_r == old_r + 1
            # new_c == old_c - 1 and new_r == old_r + 1
        # Odd old_tile.cols:
            # new_c == old_c - 1 and new_r == old_r - 1
            # new_c == old_c + 1 and new_r == old_r - 1
    # These look good on paper, but looking at the actual arrangement of
    # tiles shows them to be erroneous:
    '''
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

def load_dictionary():

    words = None

    try:
        with open('dictionary_en_US.txt') as file:
            words = file.read().split('\n')
    except FileNotFoundError:
        raise SystemExit('Error: Dictionary file not found\nExpexted file at "dictionary_en_US.txt"')
    if not words:
        raise SystemExit('Error: Dictionary file at "dictionary_en_US.txt" empty or unreadable')

    return words

def offset_from_element(element, corner, offset):

    point = [element.coords[i] + element.surf.get_size()[i] if corner[i] else element.coords[i] for i in range(len(corner))]

    return tuple([point[i] + offset[i] for i in range(len(point))])

def score_word(snake):

    value = 0
    for t in snake.tiles:
        value += t.point_value

    return value * len(snake.tiles)

def update_bomb_chance(display, last_five, snake, is_word):

    if len(last_five) > 4:
        new_five = last_five
        if is_word:
            new_five = last_five[-4:]
            new_five.append(len(''.join(snake.letters)))
        avg = round(sum(new_five) / len(new_five), 1)
        text = str(snake.get_bomb_weight(avg) * 100) + '%'
        display.update(text=text)

def update_selected_tiles(tiles, snake):

    for t in tiles:
        t.unselect()
    for t in snake.tiles:
        t.select()

def update_word_display(word_display, snake, bonus):

    color = 'red'
    text = ''
    value = 0
    is_word = False

    if snake.letters:
        word = ''.join(snake.letters)
        if len(word) > 2:
            if check_dictionary(word):
                is_word = True
                value = score_word(snake)
                if word == bonus:
                    value += len(bonus) * 10
                    color = 'gold'
                else:
                    color = 'green'

        text = f"{word} (+{value})"

    word_display.update(text=text, text_color=color)
    return is_word


def main(dims):

    global DICTIONARY

    window_surface = pygame.display.set_mode(dims)
    background = pygame.Surface(dims)
    background.fill(pygame.Color('#38424d'))

    clock = pygame.time.Clock()
    is_running = True

    # Board
    score = 0
    history = []

    board = gameboard.Board(DICTIONARY)
    coords = offset_from_element(board.bonus_display, corner=(0, 1), offset=(0, 10))
    bomb_chance_display = ui_display.UI_Display(dims=(120, 40), coords=coords, label='BOMB' ,text='--%', text_color='gray')
    coords = offset_from_element(bomb_chance_display, corner=(1, 0), offset=(10, 0))
    multiplier_display = ui_display.UI_Display(dims=(96, 40), coords=coords, label='MULT.', text='x1', text_color='gray')
    coords = offset_from_element(multiplier_display, corner=(1, 0), offset=(10, 0))
    btn_clear_marked = ui_btn.UI_Btn(btn_type='btn', dims=(100, 40), coords=coords, text='UNMARK', enabled=False)
    coords = offset_from_element(board.bonus_display, corner=(1, 0), offset=(10, 0))
    btn_scramble = ui_btn.UI_Btn(btn_type='btn', dims=(120, 40), coords=coords, text='SCRAMBLE', text_color='gray')
    coords = offset_from_element(btn_scramble, corner=(1, 0), offset=(10, 0))
    score_display = ui_display.UI_Display(dims=(180, 40), coords=coords, text='0', text_color='gray')
    coords = offset_from_element(btn_scramble, corner=(0, 1), offset=(0, 10))
    word_display = ui_display.UI_Display(dims=(310, 40), coords=coords)
    coords = offset_from_element(word_display, corner=(0, 1), offset=(0, 10))
    longest_display = ui_display.UI_Display(dims=(310, 34), coords=coords, label='LONGEST WORD', text_color='beige')
    coords = offset_from_element(longest_display, corner=(0, 1), offset=(0, 4))
    best_display = ui_display.UI_Display(dims=(310, 34), coords=coords, label='HIGHEST SCORE', text_color='beige', text_align='left', text_offset=(30, 2))
    coords = offset_from_element(best_display, corner=(0, 1), offset=(0, 4))
    word_history = ui_display.UI_Display(dims=(310, 308), coords=coords, label='WORD LIST')
    ui_elements = [score_display, word_display, word_history, btn_scramble, longest_display, best_display]
    ui_elements += [tile for tile in board.tiles]
    ui_elements += [board.bonus_display, bomb_chance_display, multiplier_display, btn_clear_marked]

    mouse_events = [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]
    mouse_down = False
    btn_down = None
    snake = tile_snake.Snake()

    word_best = None
    word_longest = ''
    last_typed = ''
    last_five = []
    is_word = False

    while is_running:

        delta = clock.tick(60)/1000.0

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                is_running = False

            elif event.type in mouse_events:
                mouse_pos = pygame.mouse.get_pos()
                active_btn = None
                try: # Get targeted button
                    for obj in ui_elements:
                        if obj.hovered:
                            obj.mouse_out()
                            last_typed = ''
                        if obj.get_abs_rect().collidepoint(mouse_pos):
                            active_btn = obj
                            active_btn.mouse_over()
                except StopIteration: # Didn't interact with a button
                    pass
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    try:
                        if active_btn.can_click:
                            btn_down = active_btn
                    except AttributeError: # Click outside UI elements
                        pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                    if btn_down and active_btn == btn_down:
                        if active_btn == btn_scramble:
                            do_scramble(snake, board)
                            last_typed = ''
                        elif active_btn == btn_clear_marked:
                            do_clear()
                            last_typed = ''
                        else:
                            # If the clicked tile is already selected, and
                            # the last tile in the snake, submit the word.
                            # Otherwise, if it's selected but not the last,
                            # unselect it and 'trim' the tile snake back to
                            # that tile (leaving it selected).
                            if active_btn.selected:
                                if active_btn == snake.tiles[-1]:
                                    # When only 1 tile is selected, clicking
                                    # it again deselects it.
                                    if len(snake.tiles) == 1:
                                        snake.new()
                                    # When 2 tiles are selected, clicking the
                                    # final tile does nothing; 3 is the
                                    # minimum word length.
                                    elif len(snake.tiles) > 2 or len(snake.tiles) == 2 and 'QU' in snake.letters:
                                        word = ''.join(snake.letters)
                                        if check_dictionary(word):
                                            value = score_word(snake)
                                            history_word = {
                                                'word': word,
                                                'value': value,
                                                'colors': ['beige' for _ in range(len(word))]
                                            }
                                            history.append(history_word)
                                            if word == board.bonus:
                                                # Color all letters blue
                                                history[-1]['colors'] = ['green' for _ in range(len(word))]
                                                value += board.bonus_counter * 10
                                                history[-1]['value'] = value
                                                board.bonus_counter += 1
                                                board.set_bonus(DICTIONARY)
                                            score += value
                                            score_display.update(text=score)

                                            history[-1] = color_letters(snake.tiles, history[-1])
                                            word_history.set_multiline_text(history)
                                            word_best = check_best(word_best, history[-1])
                                            best_display.update(multicolor_text=word_best)
                                            word_longest = check_longest(word_longest, history[-1])
                                            longest_display.update(text=word_longest)
                                            snake.reroll()
                                            last_five = [len(h['word']) for h in history[-5:]]
                                            snake.rebuild(value, last_five)
                                            board.reset_rows()
                                            last_typed = ''
                                            board.update_bombs(snake.tiles)
                                        else:
                                            print(f'Word "{word}" not in dictionary')
                                        snake.new()
                                else:
                                    snake.trim_to(active_btn)
                            # Otherwise, check if the new tile is a neighbor
                            # of the last selected tile. If so, add it;
                            # if not, start a new snake on this tile.
                            else:
                                if len(snake.tiles):
                                    if is_neighbor(active_btn, snake.tiles[-1]):
                                        snake.add(active_btn)
                                    else:
                                        snake.new(active_btn)
                                else:
                                    snake.new(active_btn)

                        is_word = update_word_display(word_display, snake, board.bonus)
                        update_selected_tiles(board.tiles, snake)
                        update_bomb_chance(bomb_chance_display, last_five, snake, is_word)

                    btn_down = None

            elif event.type == pygame.KEYDOWN:
                last_typed = board.highlight_tiles_from_letter(board.tiles, event.key, last_typed)

        board.animate()

        window_surface.blit(background, (0, 0))
        for element in ui_elements:
            window_surface.blit(element.btn, element.coords)

        pygame.display.update()

if __name__ == '__main__':

    dims = (677, 504)

    global DICTIONARY

    DICTIONARY = load_dictionary()

    pygame.init()
    pygame.display.set_caption('Booksnake')

    main(dims)

    #TODO:
        # Add "chain" multiplier somehow?
        # Click-and-drag tiles to select; release to submit
        # Setup ui_btn and ui_display to inherit common attributes from single parent class
        # Save best score & word list
        # Right click a tile to mark it ("Save me!")
            # And clear btn
        # Change border around word preview when it's a word / not a word / is the bonus word
    # Add
        #
    # Remove
        #
