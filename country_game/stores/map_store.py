import os
import pickle

import pygame

from country_game import config
from country_game.texture_loadger import TextureLoader


texture_loader = TextureLoader()


class MapStore:
    def __init__(self, maps_dir: str):
        self.maps_dir = maps_dir

    def load_maps(self, maps_group_name: str, start_coord=(0, 0)):
        maps_group_name = maps_group_name.replace('_', '-')
        return MapGroup(maps_group_name, start_coord)


class TextureObject(pygame.sprite.Sprite):
    def __init__(self, coord: list[int, int], texture_name: str):
        super().__init__()
        self.coord = coord
        self.image = texture_loader.get_texture(texture_name)
        self.set_rect_and_coord()

    def update(self):
        pass

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (config.WIDTH / 2, config.HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]


class MapGroup:
    def __init__(self, map_name: str, start_coord: tuple[int, int]):
        self.__map_name = map_name
        self.__dict_map_coord = self.__create_map_dict()
        self.coord = list(start_coord)
        self.__cached_coord = None
        self.__cached_map = None

    def get_current_map(self):
        return self.__dict_map_coord[tuple(self.coord)]

    def _load_map(self, path: str):
        with open(path, 'rb') as map_file:
            names_map = pickle.load(map_file)
        return names_map

    def can_coord_be(self, coord):
        return coord in self.__dict_map_coord.keys()

    def __create_map_dict(self):
        map_dict = {}
        for root, dirs, files in os.walk('res/compiled_maps'):
            for file in files:
                if file.startswith(self.__map_name) and file.endswith(
                        '.pickle'
                ):
                    print('load map:', file)
                    coord = tuple(map(int, file[:-7].split('_')[1:]))
                    block_names_map = self._load_map(os.path.join(root, file))
                    map_dict[coord] = self.block_names_to_sprites(
                        block_names_map
                        )
        return map_dict

    def block_names_to_sprites(self, block_names_map):
        block_group = pygame.sprite.Group()
        for i, line in enumerate(block_names_map):
            for j, block_name in enumerate(line):
                if block_name is not None:
                    block_group.add(
                        TextureObject(
                            [j * config.BLOCK_SIZE, i * config.BLOCK_SIZE],
                            block_name
                        )
                    )
        return block_group
