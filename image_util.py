import os

import pygame
from PIL import Image

BLOCK_SIZE = 50


class ResizeImg:
    def __init__(self, filename, ):
        self.filename = filename
        self.img = Image.open(filename)

    def by_width(self, value):
        self.resize(w=value)
        return self

    def by_height(self, value):
        self.resize(h=value)
        return self

    def resize(self, w=None, h=None):
        if w is not None and h is None:
            self.__resize(w, False)
        elif w is None and h is not None:
            self.__resize(h, True)
        return self

    def __resize(self, n: int, is_height: bool):
        ratio = n / self.img.size[is_height]
        width = int(self.img.size[not is_height] * ratio)
        self.img = self.img.resize((n, width), Image.AFFINE)
        return self

    def save(self, postfix='_resize.png'):
        self.img.save(self.filename + postfix)
        return self.filename + postfix


class TextureLoader:
    postfix = '_resize.png'

    def __init__(self):
        game_folder = './'
        self.img_folder = os.path.join(game_folder, 'res', 'images')

    def get_textures(self, folder, size=BLOCK_SIZE):
        local_folder = os.path.join(self.img_folder, folder)
        img_list = []

        for i in os.walk(os.path.join(local_folder)):
            for j in i[-1]:
                if j.endswith(self.postfix):
                    continue
                resize_img = ResizeImg(os.path.join(local_folder, j)).by_width(size).save(self.postfix)
                img_list.append(pygame.image.load(resize_img).convert())
        assert len(img_list) != 0, f'Не найдено текстур в папке {folder}'
        return img_list

    def get_person_textures(self, folder):
        left = []
        right = []
        bottom = []
        up = []
        for side_folder, lst in (('bottom', bottom), ('up', up), ('right', right), ('left', left)):
            local_folder = os.path.join(self.img_folder, folder, side_folder)
            for i in os.walk(os.path.join(local_folder)):
                for j in sorted(i[-1]):
                    if 'resize' in j:
                        continue
                    path = os.path.join(local_folder, j)
                    resize_img = ResizeImg(path).by_width(BLOCK_SIZE).save(self.postfix)
                    lst.append(pygame.image.load(resize_img).convert())
        return [bottom, up, right, left]