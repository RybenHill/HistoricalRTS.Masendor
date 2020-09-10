import pygame
import pygame.freetype

from RTS import mainmenu

main_dir = mainmenu.main_dir
SCREENRECT = mainmenu.SCREENRECT

class map(pygame.sprite.Sprite):
    images = []

    def __init__(self, scale):
        """image file of map should be at size 1000x1000 then it will be scaled in game"""
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.scale = scale
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.rect = self.image.get_rect(topleft=(0,0))

    def changescale(self,scale):
        self.scale = scale
        self.image = self.image_original
        scalewidth = self.image.get_width() * self.scale
        scaleheight = self.image.get_height() * self.scale
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    # def update(self, dt, pos, scale):

class mapfeature(pygame.sprite.Sprite):
    images = []

    def __init__(self, x, y, image):
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
# Surface.get_at((x, y)) ##get colour at pos maybe can be used to create map from just picture?
