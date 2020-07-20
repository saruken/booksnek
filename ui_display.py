import pygame, pygame_gui
from math import floor

class UI_Display():

    def __init__(self, manager, dims, coords, text):

        self.colors = {
            'black': pygame.Color('#000000'),
            'border_active': pygame.Color('#0000ff'),
            'border_inactive': pygame.Color('#bfb9a8'),
            'bg_bomb': pygame.Color('#202d36'),
            'bg_normal': pygame.Color('#c1a663'),
            'bg_normal_selected': pygame.Color('#f0d081'),
            'bg_gold': pygame.Color('#ebc334'),
            'bg_gold_selected': pygame.Color('#fcde72'),
            'bg_crystal': pygame.Color('#349eeb'),
            'bg_crystal_selected': pygame.Color('#76bff5')
        }
        self.fonts = {
            'btn': pygame.font.Font('VCR_OSD_MONO.ttf', 18),
            'letter': pygame.font.Font('VCR_OSD_MONO.ttf', 36),
            'point_value': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }

        self.coords = coords
        self.dims = dims
        self.manager = manager
        self.surf = pygame.Surface(self.dims)
        self.text = text

        self.build_image()
        self.build_UI()

    def build_image(self):

        border_color = self.colors['bg_bomb']
        bg_color = self.colors['bg_bomb']

        self.surf.fill(border_color)
        pygame.draw.rect(self.surf, bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        surf = self.fonts['btn'].render(str(self.text), True, self.colors['border_inactive'], bg_color)
            # Horiz/vert align center
        offset = tuple([floor((self.surf.get_size()[i]) - surf.get_size()[i]) / 2 for i in range(2)])
        self.surf.blit(surf, dest=offset)

    def build_UI(self):

        try:
            self.btn.kill()
        except AttributeError:
            pass

        self.btn = pygame_gui.elements.UIImage(relative_rect=pygame.Rect(self.coords, self.surf.get_size()), image_surface=self.surf, manager=self.manager)

    def update(self, text):

        self.text = text
        self.build_image()
        self.build_UI()
