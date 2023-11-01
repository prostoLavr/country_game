import pygame


class Item(pygame.sprite.Sprite):
    def __init__(self, coord, max_seed=3):
        pygame.sprite.Sprite.__init__(self)
        self.coord = coord

    def update(self):
        pass

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]