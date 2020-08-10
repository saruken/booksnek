import pygame

import game_logic
from ui import Tile

def load_dictionary():
    words = None

    try:
        with open('dictionary_en_US.txt') as file:
            words = file.read().split('\n')
    except FileNotFoundError:
        raise SystemExit('Error: Dictionary file not found\nExpexted file at "dictionary_en_US.txt"')
    if not words:
        raise SystemExit('Error: Dictionary file at "dictionary_en_US.txt" is empty or unreadable')

    return words

def main():
    dims = (676, 564)
    pygame.init()
    pygame.display.set_caption('Booksnake')
    window_surface = pygame.display.set_mode(dims)
    game = game_logic.Game(dims=dims, dictionary=load_dictionary())

    mouse_events = [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]
    mouse_down = False
    active_btn = None
    btn_down = None
    btn_down_right = None

    clock = pygame.time.Clock()
    is_running = True

    while is_running:

        delta = clock.tick(60)/1000.0

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                is_running = False

            elif event.type in mouse_events:
                mouse_pos = pygame.mouse.get_pos()
                active_btn = None
                try: # Get targeted button
                    for obj in [e for e in game.ui_elements if e.interactive]:
                        if obj.hovered:
                            obj.mouse_out()
                            game.last_typed = ''
                        if obj.get_abs_rect().collidepoint(mouse_pos):
                            active_btn = obj
                            active_btn.mouse_over()
                except StopIteration: # Didn't interact with a button
                    pass
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                    try:
                        if event.__dict__['button'] == 1:
                            btn_down = active_btn
                        elif event.__dict__['button'] == 3:
                            btn_down_right = active_btn
                    except AttributeError: # Click outside UI elements
                        pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.__dict__['button'] == 1:
                        mouse_down = False
                        if btn_down and active_btn == btn_down:
                            if active_btn == game.board.menu_new:
                                game.new_game()
                            elif active_btn == game.board.menu_open:
                                game.load_game()
                            elif active_btn == game.board.menu_save:
                                if menu_save.enabled:
                                    game.save_game()
                            elif active_btn == game.board.btn_scramble:
                                game.scramble()
                                game.last_typed = ''
                            elif active_btn == game.board.btn_clear_marked:
                                if game.board.btn_clear_marked.enabled:
                                    game.clear_marked()
                                    game.board.btn_clear_marked.update()
                                    game.last_typed = ''
                            else:
                                # If the clicked tile is already selected, and
                                # the last tile in the snake, submit the word.
                                # Otherwise, if it's selected but not the last,
                                # unselect it and 'trim' the tile snake back to
                                # that tile (leaving it selected).
                                if active_btn.selected:
                                    if active_btn == game.snake.last:
                                        # When only 1 tile is selected,
                                        # clicking it again deselects it.
                                        if game.snake.length == 1:
                                            game.empty_snake()
                                        # When 2 tiles are selected, clicking
                                        # the final tile does nothing; 3 is the
                                        # minimum word length.
                                        elif game.snake.length > 2:
                                            if game.check_dictionary():
                                                game.commit_word_to_history()
                                                game.score += game.score_word()
                                                game.update_score_display()
                                                game.update_history_display()
                                                game.check_update_best()
                                                game.check_update_longest()
                                                if game.snake.word == game.bonus_word:
                                                    game.mult_up()
                                                    game.update_mult_display()
                                                    game.choose_bonus_word()
                                                    game.update_bonus_display()
                                                else:
                                                    game.apply_level_progress()
                                                if game.check_level_progress():
                                                    game.level_up()
                                                game.reroll_snake_tiles()
                                                game.update_tile_rows()
                                                game.last_typed = ''
                                            else:
                                                print(f'Word "{game.snake.word}" not in dictionary')
                                            game.empty_snake()
                                            game.update_bomb_tiles()
                                            game.update_word_display()
                                            active_btn.mouse_out()
                                    # Player clicks on snake tile other than
                                    # the last one; trim back to this tile.
                                    else:
                                        game.trim_snake(active_btn)
                                # Otherwise, check if the new tile is a
                                # neighbor of the last selected tile. If so,
                                # add it; if not, start a new snake.
                                else:
                                    if game.snake.length:
                                        if game.board.is_neighbor(active_btn, game.snake.last):
                                            game.add_tile(active_btn)
                                        else:
                                            game.empty_snake()
                                            game.add_tile(active_btn)
                                    else:
                                        game.add_tile(active_btn)
                            game.update_word_display()
                            game.highlight_selected_tiles()
                            game.update_level_progress()
                        btn_down = None
                    elif event.__dict__['button'] == 3:
                        if btn_down_right and active_btn == btn_down_right:
                            if isinstance(active_btn, Tile):
                                active_btn.toggle_mark()
                        btn_down_right = None
                    game.update_btn_clear_marked()
            elif event.type == pygame.KEYDOWN:
                last_typed = game.highlight_tiles_from_letter(event.key, game.last_typed)

            game.update_tiles()

        game.animate()
        window_surface.blit(game.board.background, (0, 0))
        for element in game.ui_elements:
            window_surface.blit(element.surf, element.coords)
        pygame.display.update()

if __name__ == '__main__':

    main()

    #TODO:
        # Big refactor
            # The "progress" meter should be for "levels", which should act as separate multipliers. So a word is scored by sum(letters) * mult * lv
                # Don't reset progress when mult increases
                # Don't increase mult when lv increases
                # Replace "bomb chance" with Lv display
        # Click-and-drag tiles to select; release to submit
        # Bonuses for making shapes with the tiles in a word would be neat
        # Tie animation speed to delta
        # Controller support!

    # Add
        #
    # Remove
        #
