import pygame
from math import floor

class UI_Display():

    def __init__(self, dims, coords, label='', text='', text_align='center', text_color='black', text_offset=(0, 0)):

        self.colors = {
            'beige': pygame.Color('#aaaa66'),
            'black': pygame.Color('#000000'),
            'border_active': pygame.Color('#0000ff'),
            'border_dark': pygame.Color('#202d36'),
            'bg_bomb': pygame.Color('#21282d'),
            'bg_normal': pygame.Color('#c1a663'),
            'bg_normal_selected': pygame.Color('#f0d081'),
            'bg_gold': pygame.Color('#ebc334'),
            'bg_gold_selected': pygame.Color('#fcde72'),
            'bg_crystal': pygame.Color('#349eeb'),
            'bg_crystal_selected': pygame.Color('#76bff5'),
            'dark_gray': pygame.Color('#546c7a'),
            'gold': pygame.Color('#fce803'),
            'gray': pygame.Color('#bfb9a8'),
            'green': pygame.Color('#65a669'),
            'ocean': pygame.Color('#244254'),
            'red': pygame.Color('#e05a41'),
            'teal': pygame.Color('#50aef2')
        }
        self.fonts = {
            'btn': pygame.font.Font('VCR_OSD_MONO.ttf', 18),
            'letter': pygame.font.Font('VCR_OSD_MONO.ttf', 36),
            'point_value': pygame.font.Font('VCR_OSD_MONO.ttf', 12)
        }

        self.bg_color = self.colors['bg_bomb']
        self.border_color = self.colors['dark_gray']
        self.can_click = False
        self.can_hover = False
        self.coords = coords
        self.dims = dims
        self.hovered = False
        self.label = label
        self.surf = pygame.Surface(self.dims)
        self.text = text
        self.text_align = text_align
        self.text_color = self.colors[text_color]
        self.text_offset = text_offset

        self.btn = pygame.Surface(self.dims)
        self.build_image()
        self.build_UI()

    def build_image(self, border_color=None):

        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))
        surf = self.fonts['btn'].render(str(self.text), True, self.text_color, self.bg_color)
        # Horiz align
        if self.text_align == 'left':
            offset_x = self.text_offset[0]
        elif self.text_align == 'center':
            offset_x = floor((self.surf.get_size()[0] - surf.get_size()[0]) / 2) + self.text_offset[0]
        else:
            offset_x = self.surf.get_size()[0] - surf.get_size()[0] + self.text_offset[0]
        # Vert align
        offset_y = floor((self.surf.get_size()[1] - surf.get_size()[1]) / 2) + self.text_offset[1]
        self.surf.blit(surf, dest=(offset_x, offset_y))

        if self.label:
            text = self.fonts['point_value'].render(str(self.label), True, self.colors['dark_gray'], self.bg_color)
            surf = pygame.Surface((text.get_size()[0] + 20, text.get_size()[1]))
            surf.fill(self.bg_color)
            surf.blit(text, (10, 0))
            self.surf.blit(surf, (14, -2))

    def build_UI(self):

        self.btn.blit(self.surf, (0, 0))

    def get_abs_rect(self):

        return pygame.Rect(self.coords, self.dims)

    def mouse_out(self):

        if self.can_hover:
            self.hovered = False
            self.build_image()
            self.build_UI()

    def mouse_over(self):

        if self.can_hover:
            self.hovered = True
            self.build_image(border_color=self.colors['border_active'])
            self.build_UI()

    def set_multiline_text(self, history):

        '''
        Items in the 'history' list are dicts. They have the following keys:
            word   - Word (str)
            value  - Point value (int)
            colors - Letter colors (list of strings):
        '''
        text = ''
        text_offset = (8, 8)
        letter_height = 0
        letter_width = 0

        self.surf.fill(self.border_color)
        pygame.draw.rect(self.surf, self.bg_color, pygame.Rect((2, 2), (self.dims[0] - 4, self.dims[1] - 4)))

        for index_hist, d in enumerate(history):
            for index_letter, letter in enumerate(d['word']):
                surf = self.fonts['btn'].render(letter, True, self.colors[d['colors'][index_letter]], self.bg_color)
                if not letter_width:
                    letter_width = surf.get_size()[0]
                if not letter_height:
                    letter_height = surf.get_size()[1]
                offset = (text_offset[0] + letter_width * index_letter, text_offset[1] + letter_height * index_hist)
                self.surf.blit(surf, dest=offset)

                if index_letter == len(d['word']) - 1:
                    surf = self.fonts['btn'].render(f' (+{d["value"]})', True, self.colors['beige'], self.bg_color)
                    offset = (text_offset[0] + letter_width * (index_letter + 1), text_offset[1] + letter_height * index_hist)
                    self.surf.blit(surf, dest=offset)

        self.build_UI()

    def update(self, text=None, text_color=None):

        if text_color:
            self.text_color = self.colors[text_color]
        if text != None:
            self.text = text
        self.build_image()
        self.build_UI()
