from math import sqrt

import pygame

from country_game.texture_loadger import TextureLoader
from country_game import config
from country_game.config import DedMoveFlags
from country_game.config import MoveSide


texture_loader = TextureLoader()


class Ded(pygame.sprite.Sprite):
    DED_WIDTH = 50
    DED_SPEED = 7
    DED_CROSS_SPEED = DED_SPEED * sqrt(2)
    DED_STEP_SPEED = 4  # When less number then faster steps.

    def __init__(self, coord):
        pygame.sprite.Sprite.__init__(self)
        self.now = 0
        self.texture = texture_loader.get_person_textures('ded')
        self.image = self.texture[0][0]
        self.image.set_colorkey(config.BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (config.WIDTH / 2, config.HEIGHT / 2)

        self.coord = coord
        self.step = False
        self.side = 0

    def go_by_move_flags_object(self, ded_move_flags: DedMoveFlags):
        self.go_by_flags(
            ded_move_flags.forward, ded_move_flags.backward,
            ded_move_flags.left, ded_move_flags.right
        )

    def go_by_flags(self, forward, backward, left, right):
        if left:
            self.coord[
                0] -= self.DED_SPEED if forward or backward else (
                self.DED_CROSS_SPEED)
            self.side = MoveSide.LEFT
        if right:
            self.coord[
                0] += self.DED_SPEED if forward or backward else (
                self.DED_CROSS_SPEED)
            self.side = MoveSide.RIGHT
        if forward:
            self.coord[
                1] += self.DED_SPEED if left or right else self.DED_CROSS_SPEED
            self.side = MoveSide.FORWARD
        if backward:
            self.coord[
                1] -= self.DED_SPEED if left or right else self.DED_CROSS_SPEED
            self.side = MoveSide.BACKWARD
        self.step = any((left, right, forward, backward))

    def update(self, map_group):
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]
        if self.step:
            self.now = (self.now + 1) % ((len(
                self.texture[self.side][1:]
            )) * self.DED_STEP_SPEED)
            self.image = self.texture[self.side][1:][
                self.now // self.DED_STEP_SPEED]
        else:
            self.now = 0
            self.image = self.texture[self.side][0]
        self.image.set_colorkey(config.BACKGROUND_COLOR)
        x, y = map_group.coord
        if self.rect.right > config.WIDTH:
            if map_group.can_coord_be((x, y + 1)):
                if self.rect.left > config.WIDTH:
                    self.rect.x = self.coord[0] = 0
                    map_group.coord = (x, y + 1)
            else:
                self.coord[0] = config.WIDTH - self.rect.width

        if self.rect.left < 0:
            if map_group.can_coord_be((x, y - 1)):
                if self.rect.right < 0:
                    self.rect.x = self.coord[0] = config.WIDTH - self.rect.width
                    map_group.coord = (x, y - 1)
            else:
                self.coord[0] = 0

        if self.rect.bottom > config.HEIGHT:
            if map_group.can_coord_be((x + 1, y)):
                if self.rect.top > config.HEIGHT:
                    self.rect.y = self.coord[1] = 0
                    map_group.coord = (x + 1, y)
            else:
                self.coord[1] = config.HEIGHT - self.rect.height

        if self.rect.top < 0:
            if map_group.can_coord_be((x - 1, y)):
                if self.rect.bottom < 0:
                    self.rect.y = self.coord[
                        1] = config.HEIGHT - self.rect.height
                    map_group.coord = (x - 1, y)
            else:
                self.coord[1] = 0

        self.step = False

        # if pygame.sprite.spritecollide(self,
        # game_obj.world.get_objects_draw(), False):
        #     for i in pygame.sprite.spritecollide(self,
        #     game_obj.world.get_objects_draw(), False):
        #         if isinstance(i, Item):
        #             self.inventory.addItem(i)
        #             self.world.objects[self.world.y][self.world.x].remove(i)
        #             game_obj.items_group.remove(i)

    def save_preload(self):
        self.texture = None
        self.image = None
        return self
