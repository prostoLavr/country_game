import random

import pygame

from country_game import config


class Plant(pygame.sprite.Sprite):
    def __init__(self, coord, max_seed=3):
        pygame.sprite.Sprite.__init__(self)
        self.seed = random.randint(0, max_seed)
        self.coord = coord
        self.n_grow = 0

    def grow(self):
        self.n_grow += config.GROW_SPEED

    def update(self):
        pass

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (config.WIDTH / 2, config.HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]
