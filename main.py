import os
import random

import dill
import pygame
from PIL import Image

import blocks


GROW_SPEED = 10
BLOCK_SIZE = 50

WIDTH = 750
HEIGHT = 500
FPS = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FORWARD = 0
BACKWARD = 1
RIGHT = 2
LEFT = 3

BACKGROUND_COLOR = (237, 48, 48)

DED_WIDTH = 50
DED_SPEED = 5
DED_STEP_SPEED = 5  # The less number the faster steps.

OPEN_SAVE = True
FILE_SAVE = 'save'

WORLD_MAP = blocks.map_lst

if OPEN_SAVE:
    with open(FILE_SAVE, 'rb') as file:
        LOAD_DATA = dill.load(file)


class ResizeImg:
    def __init__(self, filename, w=None, h=None):
        self.filename = filename
        img = Image.open(filename)
        if w is not None and h is None:
            ratio = (w / float(img.size[0]))
            height = int((float(img.size[1]) * float(ratio)))
            img = img.resize((w, height), Image.AFFINE)
        elif w is None and h is not None:
            ratio = (h / float(img.size[1]))
            width = int((float(img.size[0]) * float(ratio)))
            img = img.resize((h, width), Image.AFFINE)
        img.save(filename + '_resize.png')

    def get_filename(self):
        return self.filename + '_resize.png'


class World:
    def __init__(self, map_dict, x=0, y=0):
        self.x = x
        self.y = y
        self.generate(map_dict)

    def generate(self, map_dict):
        obj_map_list = []
        up_obj_map_list = []
        for y_world, value1 in enumerate(map_dict):
            tmp_lst2 = []
            for x_world, value2 in enumerate(value1):
                tmp_lst1 = []
                for i, v in enumerate(value2):
                    tmp_lst = []
                    for j, obj_str in enumerate(v):
                        if obj_str == 'grass':
                            tmp_lst.append(Grass([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                        if obj_str == 'ground':
                            tmp_lst.append(Ground([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                        if obj_str == 'house':
                            up_obj_map_list.append(House([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                    tmp_lst1.append(tmp_lst)
                tmp_lst2.append(tmp_lst1)
            obj_map_list.append(tmp_lst2)
        self.obj_map_list = obj_map_list
        self.up_obj_map_list = up_obj_map_list

    def get_lst(self):
        return self.obj_map_list[self.y][self.x]

    def right(self):
        self.x += 1

    def is_right(self):
        if self.x < 1:
            return True
        return False

    def left(self):
        self.x -= 1

    def is_left(self):
        if self.x > 0:
            return True
        return False

    def up(self):
        self.y += 1

    def is_up(self):
        if self.y < 1:
            return True
        return False

    def down(self):
        self.y -= 1

    def is_down(self):
        if self.y > 0:
            return True
        return False


class Plant(pygame.sprite.Sprite):
    def __init__(self, coord):
        pygame.sprite.Sprite.__init__(self)
        self.seed = random.randint(0, 3)
        self.coord = coord
        self.n_grow = 0

    def grow(self):
        self.n_grow += GROW_SPEED

    def update(self):
        pass

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]


class Grass(Plant):
    def __init__(self, *args):
        Plant.__init__(self, *args)
        self.image = TextureLoader().get_textures('grass')[self.seed // 2]
        self.set_rect_and_coord()


class Ground(Plant):
    def __init__(self, *args):
        Plant.__init__(self, *args)
        self.image = TextureLoader().get_textures('ground')[0]
        self.set_rect_and_coord()


class House(pygame.sprite.Sprite):
    def __init__(self, coord):
        pygame.sprite.Sprite.__init__(self)
        self.coord = coord
        self.image = TextureLoader().get_textures('house', 150)[0]
        self.set_rect_and_coord()

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]


class Ded(pygame.sprite.Sprite):
    def __init__(self, coord, world_obj: World):
        pygame.sprite.Sprite.__init__(self)
        self.now = 0
        self.texture = TextureLoader().get_person_textures('ded')
        self.image = self.texture[0][0]
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.world = world_obj
        self.coord = coord
        self.step = False
        self.side = 0

    def go_forward(self, delta):
        self.coord[1] += delta
        self.step = True
        self.side = FORWARD

    def go_backward(self, delta):
        self.coord[1] -= delta
        self.step = True
        self.side = BACKWARD

    def go_left(self, delta):
        self.coord[0] -= delta
        self.step = True
        self.side = LEFT

    def go_right(self, delta):
        self.coord[0] += delta
        self.step = True
        self.side = RIGHT

    def update(self):
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]
        if self.step:
            self.now = (self.now + 1) % ((len(self.texture[self.side][1:])) * DED_STEP_SPEED)
            self.image = self.texture[self.side][1:][self.now // DED_STEP_SPEED]
        else:
            self.now = 0
            self.image = self.texture[self.side][0]
        self.image.set_colorkey(BACKGROUND_COLOR)

        if self.rect.right > WIDTH:
            if self.world.is_right():
                if self.rect.left > WIDTH:
                    self.coord[0] = 0
                    self.rect.x = self.coord[0]
                    self.world.right()
            else:
                self.coord[0] = WIDTH - self.rect.width

        if self.rect.left < 0:
            if self.world.is_left():
                if self.rect.right < 0:
                    self.coord[0] = WIDTH - self.rect.width
                    self.rect.x = self.coord[0]
                    self.world.left()
            else:
                self.coord[0] = 0

        if self.rect.bottom > HEIGHT:
            if self.world.is_up():
                if self.rect.top > HEIGHT:
                    self.coord[1] = 0
                    self.rect.y = self.coord[1]
                    self.world.up()
            else:
                self.coord[1] = HEIGHT - self.rect.height

        if self.rect.top < 0:
            if self.world.is_down():
                if self.rect.bottom < 0:
                    self.coord[1] = HEIGHT - self.rect.height
                    self.rect.y = self.coord[1]
                    self.world.down()
            else:
                self.coord[1] = 0

        self.step = False

    def save_preload(self):
        self.texture = None
        self.image = None
        return self


class TextureLoader:
    def __init__(self):
        game_folder = os.path.dirname(__file__)
        self.img_folder = os.path.join(game_folder, 'res', 'images')

    def get_textures(self, folder, size=BLOCK_SIZE):
        local_folder = os.path.join(self.img_folder, folder)
        img_list = []
        for i in os.walk(os.path.join(local_folder)):
            for j in i[-1]:
                if 'resize' not in j:
                    ResizeImg(os.path.join(local_folder, j), w=size).get_filename()
                    resize_img = os.path.join(local_folder, j + '_resize.png')
                    img_list.append(pygame.image.load(resize_img).convert())
        return img_list

    def get_person_textures(self, folder):
        left_list = []
        right_list = []
        forward_list = []
        backward_list = []
        for side_folder in ['forward', 'backward', 'right', 'left']:
            local_folder = os.path.join(self.img_folder, folder, side_folder)
            for i in os.walk(os.path.join(local_folder)):
                for j in sorted(i[-1]):
                    if 'resize' not in j:
                        ResizeImg(os.path.join(local_folder, j), w=BLOCK_SIZE).get_filename()
                        resize_img = os.path.join(local_folder, j + '_resize.png')
                        if 'forward' == side_folder:
                            forward_list.append(pygame.image.load(resize_img).convert())
                        if 'backward' == side_folder:
                            backward_list.append(pygame.image.load(resize_img).convert())
                        if 'right' == side_folder:
                            right_list.append(pygame.image.load(resize_img).convert())
                        if 'left' == side_folder:
                            left_list.append(pygame.image.load(resize_img).convert())
        return [forward_list, backward_list, right_list, left_list]


class Game:
    def __init__(self):
        self.init_game()
        self.game_loop()

    def init_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.ded_grp = pygame.sprite.Group()
        self.world = World(WORLD_MAP, *LOAD_DATA[1])
        self.ded_init()

    def ded_init(self):
        if LOAD_DATA is not None:
            self.ded = Ded(LOAD_DATA[0], self.world)
        else:
            self.ded = Ded([100, 100], self.world)
        self.ded_grp.add(self.ded)

    # Обработка событий
    def game_loop(self):
        left_flag = False
        right_flag = False
        forward_flag = False
        backward_flag = False
        running = True
        while running:
            map_now = pygame.sprite.Group()
            for i in self.world.get_lst():
                for j in i:
                    map_now.add(j)
            map_now.update()
            self.ded_grp.update()
            self.screen.fill(WHITE)
            map_now.draw(self.screen)
            self.ded_grp.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open(FILE_SAVE, 'wb') as file:
                        dill.dump([self.ded.coord, [self.world.x, self.world.y]],
                                  file, protocol=dill.HIGHEST_PROTOCOL)
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        left_flag = True
                    if event.key == pygame.K_UP:
                        forward_flag = True
                    if event.key == pygame.K_DOWN:
                        backward_flag = True
                    if event.key == pygame.K_RIGHT:
                        right_flag = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        left_flag = False
                    if event.key == pygame.K_UP:
                        forward_flag = False
                    if event.key == pygame.K_DOWN:
                        backward_flag = False
                    if event.key == pygame.K_RIGHT:
                        right_flag = False
            if left_flag:
                self.ded.go_left(DED_SPEED)
            if right_flag:
                self.ded.go_right(DED_SPEED)
            if forward_flag:
                self.ded.go_backward(DED_SPEED)
            if backward_flag:
                self.ded.go_forward(DED_SPEED)

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    pygame.quit()
