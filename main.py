import pygame

import game_logic
from ui import Tile, HPDisplay

def get_elem_under_mouse(game):
    mouse_pos = pygame.mouse.get_pos()
    for obj in [e for e in game.ui_elements if e.interactive]:
        if obj.get_abs_rect().collidepoint(mouse_pos):
            return obj
    return None

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
    dims = (676, 608)
    pygame.init()
    pygame.display.set_caption('Booksnek')
    window_surface = pygame.display.set_mode(dims)
    game = game_logic.Game(dims=dims, dictionary=load_dictionary())

    mouse_down = pygame.MOUSEBUTTONDOWN
    mouse_up = pygame.MOUSEBUTTONUP
    mouse_motion = pygame.MOUSEMOTION
    mouse_left = 1
    mouse_right = 3
    left_clicked_elem = None
    right_clicked_elem = None
    begin_submit = False
    mode = 'click'
    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        clock.tick(60)
        game.board.gfx.fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == mouse_down:
                elem = get_elem_under_mouse(game)
                if event.__dict__['button'] == mouse_left:
                    left_clicked_elem = elem
                    if isinstance(elem, Tile):
                        mode = 'drag'
                        begin_submit = bool(elem == game.snake.last)
                        game.try_add_tile(elem)
                        game.update_word_display()
                        game.highlight_selected_tiles()
                elif event.__dict__['button'] == mouse_right:
                    right_clicked_elem = elem
            elif event.type == mouse_up:
                elem = get_elem_under_mouse(game)
                if event.__dict__['button'] == mouse_left:
                    if elem in game.board.menu_btns:
                        if elem == left_clicked_elem:
                            game.handle_menu_btn_click(elem)
                    else:
                        if not game.paused:
                            if elem == left_clicked_elem:
                                if begin_submit:
                                    game.try_submit_word()
                                else:
                                    game.try_add_tile(elem)
                            else:
                                game.try_submit_word()
                            game.update_word_display()
                            game.update_bonus_display()
                            game.highlight_selected_tiles()
                            game.update_btn_clear_marked()
                        mode = 'click'
                elif event.__dict__['button'] == mouse_right:
                    game.toggle_mark(elem, right_clicked_elem)
            elif event.type == mouse_motion:
                elem = get_elem_under_mouse(game)
                game.try_mouse_over(elem)
                if mode == 'drag':
                    game.try_add_tile(elem)
                    game.update_word_display()
                    game.highlight_selected_tiles()
            elif event.type == pygame.KEYDOWN:
                if not game.paused:
                    last_typed = game.highlight_tiles_from_letter(event.key, game.last_typed)
            game.update_btn_clear_marked()
        game.animate()
        window_surface.blit(game.board.background, (0, 0))
        for element in game.ui_elements:
            window_surface.blit(element.surf, element.coords)
        game.board.gfx.blit_gfx(window_surface)
        pygame.display.update()

if __name__ == '__main__':
    main()

    #TODO:
        # Make atk tiles flash on (1)
        # Possible bug:
            # Set up
                # Heal tile in snake
                # HP + heal < max
                # Score from word will advance beyond next level
            # Result
                # Seems like the HP delta boost from levelling is healing more than it should in this case?
        # Achievements for making shapes with tiles
        # Controller support!

    # Add words from dict
        #
    # Remove words from dict
        #
