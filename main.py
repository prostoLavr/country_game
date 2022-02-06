import os
import random

import dill
import pygame
from PIL import Image

import blocks
import xml.etree.ElementTree as ET


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
GRAY = (60, 60, 60)
GRAY2 = (120, 120, 120)
DARKGRAY = (180, 180, 180)

FORWARD = 0
BACKWARD = 1
RIGHT = 2
LEFT = 3

BACKGROUND_COLOR = (204, 51, 51)

OPEN_SAVE = False 
FILE_SAVE = 'save'

WORLD_MAP = blocks.map_lst

if OPEN_SAVE:
    with open(FILE_SAVE, 'rb') as file:
        LOAD_DATA = dill.load(file)
else:
    LOAD_DATA = [100, 100], (0, 0)


class Plant(pygame.sprite.Sprite):
    def __init__(self, coord, max_seed=3):
        pygame.sprite.Sprite.__init__(self)
        self.seed = random.randint(0, max_seed)
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
    def __init__(self, *args, **kwargs):
        Plant.__init__(self, *args, **kwargs)
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


class World:
    def __init__(self, map_dict, x=0, y=0):
        self.x = x
        self.y = y
        self.npcs = []
        self.generate(map_dict)

    def get_npc_draw(self):
        return self.npcs[self.y][self.x]

    def generate(self, map_dict):
        obj_map_list = []
        up_obj_map_list = []
        for y_world, value1 in enumerate(map_dict):
            tmp_lst2 = []
            self.npcs.append([])
            for x_world, value2 in enumerate(value1):
                tmp_lst1 = []
                self.npcs[-1].append([])
                for i, v in enumerate(value2):
                    tmp_lst = []
                    for j, obj_str in enumerate(v):
                        if obj_str == 'grass':
                            tmp_lst.append(Grass([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                        if obj_str == 'ground':
                            tmp_lst.append(Ground([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                        if obj_str == 'house':
                            # TODO: Временно заполняется землёй
                            up_obj_map_list.append(Grass([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                            # up_obj_map_list.append(House([j * BLOCK_SIZE, i * BLOCK_SIZE]))
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


class NPC(pygame.sprite.Sprite):
    SPEED = 5
    WIDTH = 50

    def __init__(self, coord: tuple, world_obj: World, world_coord: tuple):
        """

        :param coord:
        :param world_obj:
        :param world_coord: координаты мира(World.x, World.y)
        """
        pygame.sprite.Sprite.__init__(self)
        self.texture = TextureLoader().get_person_textures('npc')
        self.image = self.texture[0][0]
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = coord
        self.step = False
        self.can_move = True
        self.side = 0

        self.point_move = None  # Точка, к которой движется

        world_obj.npcs[world_coord[1]][world_coord[0]].append(self)

    def get_dialog(self, dialog_name, p_id=1) -> dict:
        dialogs = ET.parse('dialogs.xml').getroot()
        ret = {}
        for a in dialogs:
            if a.attrib['name'] == dialog_name:
                for p in a:
                    if p.attrib['id'] == str(p_id):
                        ret['npc_object'] = self
                        ret['dialog_name'] = dialog_name
                        ret['text'] = list(p)[0].text
                        if list(p)[1] == 'exit':
                            ret['answers'] = None
                        else:
                            ret['answers'] = [{'text': ans.text, 'to': ans.attrib['to']} for ans in list(p)[1]]
                        break
            if ret:
                break
        return ret

    def move(self, direction):
        if direction == RIGHT:
            self.rect.x += NPC.SPEED
            self.step = True
            self.side = RIGHT
        elif direction == LEFT:
            self.rect.x -= NPC.SPEED
            self.step = True
            self.side = LEFT
        elif direction == FORWARD:
            self.rect.y -= NPC.SPEED
            self.step = True
            self.side = BACKWARD
        elif direction == BACKWARD:
            self.rect.y += NPC.SPEED
            self.step = True
            self.side = FORWARD

    def update(self):
        if self.can_move:
            if self.step:
                self.now = (self.now + 1) % ((len(self.texture[self.side][1:])) * Ded.DED_STEP_SPEED)
                self.image = self.texture[self.side][1:][self.now // Ded.DED_STEP_SPEED]
            else:
                self.now = 0
                self.image = self.texture[self.side][0]
            self.image.set_colorkey(BACKGROUND_COLOR)
            self.step = False

            if self.point_move:
                if self.rect.x not in range(self.point_move[0] - NPC.SPEED, self.point_move[0] + NPC.SPEED) \
                        and self.point_move[0] > self.rect.x:
                    self.move(RIGHT)
                elif self.rect.x not in range(self.point_move[0] - NPC.SPEED, self.point_move[0] + NPC.SPEED) \
                        and self.point_move[0] < self.rect.x:
                    self.move(LEFT)
                elif self.rect.y not in range(self.point_move[1] - NPC.SPEED, self.point_move[1] + NPC.SPEED) \
                        and self.point_move[1] < self.rect.y:
                    self.move(FORWARD)
                elif self.rect.y not in range(self.point_move[1] - NPC.SPEED, self.point_move[1] + NPC.SPEED) \
                        and self.point_move[1] > self.rect.y:
                    self.move(BACKWARD)
                else:
                    self.point_move = None
            else:
                self.point_move = (random.randrange(0, WIDTH - self.image.get_size()[0], NPC.SPEED),
                                   random.randrange(0, HEIGHT - self.image.get_size()[1], NPC.SPEED))


class Ded(pygame.sprite.Sprite):
    DED_WIDTH = 50
    DED_SPEED = 5
    DED_STEP_SPEED = 4  # The less number the faster steps.

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
            self.now = (self.now + 1) % ((len(self.texture[self.side][1:])) * self.DED_STEP_SPEED)
            self.image = self.texture[self.side][1:][self.now // self.DED_STEP_SPEED]
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


class Game:
    def __init__(self):
        self.dialog = None
        self.init_game()
        self.game_loop()

    def init_game(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.ded_grp = pygame.sprite.Group()
        self.npc_group = pygame.sprite.Group()
        self.world = World(WORLD_MAP, *LOAD_DATA[1])
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 22)
        self.ded_init()

    def ded_init(self):
        self.ded = Ded(LOAD_DATA[0], self.world)
        self.ded_grp.add(self.ded)
        self.npc_group.add(NPC((0, 0), self.world, (0, 0)))

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
            for n in self.world.get_npc_draw():
                n.update()
                self.screen.blit(n.image, n.rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open(FILE_SAVE, 'wb') as file:
                        dill.dump([self.ded.coord, [self.world.x, self.world.y]],
                                  file, protocol=dill.HIGHEST_PROTOCOL)
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.dialog:
                        if not self.dialog['answers']:
                            t = self.font.render(f"*окончить диалог*", True, GRAY, DARKGRAY)
                            if t.get_rect(topleft=(10, HEIGHT - 75)).collidepoint(pygame.mouse.get_pos()):
                                self.dialog['npc_object'].can_move = True
                                self.dialog = None
                        else:
                            for i, a in enumerate(self.dialog['answers']):
                                t = self.font.render(f"{i + 1}) {a['text']}", True, GRAY, DARKGRAY)
                                if t.get_rect(topleft=(10, HEIGHT - (75 - 25 * i)))\
                                        .collidepoint(pygame.mouse.get_pos()):
                                    self.dialog = self.dialog['npc_object'].get_dialog(self.dialog['dialog_name'],
                                                                                       a['to'])
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        left_flag = True
                    if event.key == pygame.K_UP:
                        forward_flag = True
                    if event.key == pygame.K_DOWN:
                        backward_flag = True
                    if event.key == pygame.K_RIGHT:
                        right_flag = True
                    if event.key == pygame.K_d:  # Начать диалог
                        if self.dialog is None:
                            dialog_npc = None
                            for n in self.world.get_npc_draw():
                                if n.rect.centerx in range(self.ded.rect.centerx - BLOCK_SIZE,
                                                           self.ded.rect.centerx + BLOCK_SIZE) \
                                        and n.rect.centery in range(self.ded.rect.centery - BLOCK_SIZE,
                                                                    self.ded.rect.centery + BLOCK_SIZE):
                                    dialog_npc = n
                                    break
                            if dialog_npc:
                                dialog_npc.can_move = False
                                self.dialog = dialog_npc.get_dialog('test')  # TODO получение диалогов нпс
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
                self.ded.go_left(Ded.DED_SPEED)
            if right_flag:
                self.ded.go_right(Ded.DED_SPEED)
            if forward_flag:
                self.ded.go_backward(Ded.DED_SPEED)
            if backward_flag:
                self.ded.go_forward(Ded.DED_SPEED)

            if self.dialog:  # Отображение диалога
                self.screen.blit(self.font.render(self.dialog['text'], True, (60, 60, 60), (180, 180, 180, 180)),
                                 (10, HEIGHT - 100))
                if not self.dialog['answers']:
                    t = self.font.render(f"*окончить диалог*", True, GRAY, DARKGRAY)
                    if t.get_rect(topleft=(10, HEIGHT - 75)).collidepoint(pygame.mouse.get_pos()):
                        t = self.font.render(f"*окончить диалог*", True, BLACK, DARKGRAY)
                    self.screen.blit(t, (10, HEIGHT - 75))
                else:
                    for i, a in enumerate(self.dialog['answers']):
                        t = self.font.render(f"{i + 1}) {a['text']}", True, GRAY, DARKGRAY)
                        if t.get_rect(topleft=(10, HEIGHT - (75 - 25 * i))).collidepoint(pygame.mouse.get_pos()):
                            t = self.font.render(f"{i + 1}) {a['text']}", True, BLACK, DARKGRAY)
                        self.screen.blit(t, (10, HEIGHT - (75 - 25 * i)))

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    pygame.quit()
