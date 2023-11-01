from typing import List, Union

import pygame
from country_game.texture_loadger import TextureLoader


class Inventory:
    inv_size = (306, 306)

    def __init__(self):
        self.image = pygame.Surface(self.inv_size)
        self.image.fill((100, 50, 100))
        self.image.set_alpha(200)
        self.slots: List[Union['Item', None]] = [None for _ in range((self.inv_size[0] // Item.item_texture_size[0]) *
                                                                     (self.inv_size[1] // Item.item_texture_size[1]))]
        self.items_font = pygame.font.Font(pygame.font.match_font('arial'), 20)

    def draw(self, screen):
        i = 0
        im = self.image.copy()
        for y in range(0, self.inv_size[1], Item.item_texture_size[1] + 1):
            for x in range(0, self.inv_size[0], Item.item_texture_size[0] + 1):
                if i > len(self.slots) - 1:
                    break
                if self.slots[i]:
                    im.blit(self.slots[i].image, (x, y))
                i += 1
        screen.blit(im, (0, 0))
        i = 0
        for y in range(0, self.inv_size[1], Item.item_texture_size[1] + 1):
            for x in range(0, self.inv_size[0], Item.item_texture_size[0] + 1):
                if i > len(self.slots) - 1 or not self.slots[i]:
                    break
                m_pos = pygame.mouse.get_pos()
                if pygame.rect.Rect(x, y, *Item.item_texture_size).collidepoint(*m_pos):
                    screen.blit(self.items_font.render(self.slots[i].name, True, (0, 0, 0), (70, 70, 70)),
                                (m_pos[0] + 15, m_pos[1] - 5))
                i += 1

    def addItem(self, item: 'Item'):
        assert isinstance(item, Item) is True
        try:
            self.slots[self.slots.index(None)] = item
        except ValueError:  # Если нет места
            pass


class Item(pygame.sprite.Sprite):
    item_texture_size = (50, 50)

    def __init__(self, name, items_group, world_obj=None, world_coord: tuple = None, coords: tuple = None):
        """

        :param name:
        :param items_group:
        :param world_obj: указывать если предмет лежит в мире
        :param world_coord: указывать если предмет лежит в мире
        :param coords: указывать если предмет лежит в мире
        """
        pygame.sprite.Sprite.__init__(self, items_group)
        # self.image = TextureLoader().get_textures(name)[0]
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.name = name

        if world_obj:
            world_obj.objects[world_coord[1]][world_coord[0]].append(self)
            self.rect.topleft = coords
