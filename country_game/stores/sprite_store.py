import pygame

from country_game.objects.ded import Ded
from country_game.objects.items import Item


class SpriteStore:
    def __init__(self):
        self.ded_group = pygame.sprite.Group()
        self.nps_group = pygame.sprite.Group()
        self.item_group = pygame.sprite.Group()

    def add_ded(self, ded: Ded):
        self.ded_group.add(ded)

    def add_item(self, item: Item):
        self.item_group.add(item)
