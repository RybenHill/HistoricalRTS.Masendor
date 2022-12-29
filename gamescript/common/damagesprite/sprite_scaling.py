import pygame


def sprite_scaling(self):
    if self.camera_scale <= 1:
        self.camera_scale = 1
        self.image = self.image_original.copy()
    else:
        self.image = pygame.transform.smoothscale(self.image_original,
                                                  (int(self.image_original.get_width() / self.camera_scale),
                                                   int(self.image_original.get_height() / self.camera_scale)))
    self.image = pygame.transform.rotate(self.image, self.angle)
    self.pos = pygame.Vector2(self.base_pos[0] * self.screen_scale[0],
                              self.base_pos[1] * self.screen_scale[1]) * self.camera_zoom
    self.rect = self.image.get_rect(center=self.pos)
