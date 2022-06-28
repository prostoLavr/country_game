import random

import dill
import pygame

import blocks
import xml.etree.ElementTree as ET
from image_util import TextureLoader
from inventory import Inventory, Item
import pickle
import os
from math import sqrt
from dataclasses import dataclass
from enum import Enum


pygame.init()


GROW_SPEED = 10
BLOCK_SIZE = pygame.display.Info().current_w // 16

WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
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


texture_loader = TextureLoader(BLOCK_SIZE)


@dataclass
class DedMoveFlags:
    left: bool
    right: bool
    forward: bool
    backward: bool


class EventProcessStatus(Enum):
    NOTHING = 0
    EXIT = 1


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
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]


class House(pygame.sprite.Sprite):
    def __init__(self, coord):
        pygame.sprite.Sprite.__init__(self)
        self.coord = coord
        self.image = texture_loader.get_textures('house', 150)[0]
        self.set_rect_and_coord()

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]


class World:
    def __init__(self, map_dict, x=0, y=0):
        self.x = x
        self.y = y
        self.objects = []
        self.generate(map_dict)

    def get_objects_draw(self) -> list:
        return self.objects[self.y][self.x]

    def generate(self, map_dict):
        obj_map_list = []
        up_obj_map_list = []
        for y_world, value1 in enumerate(map_dict):
            tmp_lst2 = []
            self.objects.append([])
            for x_world, value2 in enumerate(value1):
                tmp_lst1 = []
                self.objects[-1].append([])
                for i, v in enumerate(value2):
                    tmp_lst = []
                    for j, obj_str in enumerate(v):
                        if obj_str == 'house':
                            # TODO: Временно заполняется землёй
                            pass
                            # up_obj_map_list.append(House([j * BLOCK_SIZE, i * BLOCK_SIZE]))
                        else:
                            tmp_lst.append(TextureObject([j * BLOCK_SIZE, i * BLOCK_SIZE], obj_str))
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
        self.texture = texture_loader.get_person_textures('npc')
        self.image = self.texture[0][0]
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = coord
        self.step = False
        self.can_move = True
        self.side = 0

        self.point_move = None  # Точка, к которой движется

        world_obj.objects[world_coord[1]][world_coord[0]].append(self)

    def get_dialog(self, dialog_name, p_id=1) -> dict:
        """Получение словаря с текстом диалога

        :param p_id: пункт диалога
        """
        dialogs = ET.parse('dialogs.xml').getroot()
        ret = {}
        for a in dialogs:
            if a.attrib['name'] == dialog_name:
                for p in a:
                    if p.attrib['id'] == str(p_id):
                        ret['npc_object'] = self
                        ret['dialog_name'] = dialog_name
                        ret['text'] = list(p)[0].text
                        if list(p)[1].text == 'exit':
                            ret['answers'] = None
                        else:
                            ret['answers'] = [{'text': ans.text, 'to': ans.attrib['to']} for ans in list(p)[1]]
                        break
            if ret:
                break
        return ret

    def move(self, direction):
        self.step = True
        if direction == RIGHT:
            self.rect.x += NPC.SPEED
            self.side = RIGHT
        elif direction == LEFT:
            self.rect.x -= NPC.SPEED
            self.side = LEFT
        elif direction == FORWARD:
            self.rect.y -= NPC.SPEED
            self.side = BACKWARD
        elif direction == BACKWARD:
            self.rect.y += NPC.SPEED
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
    DED_SPEED = 7
    DED_CROSS_SPEED = DED_SPEED * sqrt(2)
    DED_STEP_SPEED = 4  # The less number the faster steps.

    def __init__(self, coord):
        pygame.sprite.Sprite.__init__(self)
        self.now = 0
        self.texture = texture_loader.get_person_textures('ded')
        self.image = self.texture[0][0]
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.coord = coord
        self.step = False
        self.side = 0
        self.inventory = Inventory()
    
    def go_by_move_flags_object(self, ded_move_flags: DedMoveFlags):
        self.go_by_flags(ded_move_flags.forward, ded_move_flags.backward, 
                         ded_move_flags.left, ded_move_flags.right)

    def go_by_flags(self, forward, backward, left, right):
        if left:
            self.coord[0] -= self.DED_SPEED if forward or backward else self.DED_CROSS_SPEED
            self.side = LEFT
        if right:
            self.coord[0] += self.DED_SPEED if forward or backward else self.DED_CROSS_SPEED
            self.side = RIGHT
        if forward:
            self.coord[1] += self.DED_SPEED if left or right else self.DED_CROSS_SPEED
            self.side = FORWARD
        if backward:
            self.coord[1] -= self.DED_SPEED if left or right else self.DED_CROSS_SPEED
            self.side = BACKWARD
        self.step = any((left, right, forward, backward))

    def update(self, map_group):
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]
        if self.step:
            self.now = (self.now + 1) % ((len(self.texture[self.side][1:])) * self.DED_STEP_SPEED)
            self.image = self.texture[self.side][1:][self.now // self.DED_STEP_SPEED]
        else:
            self.now = 0
            self.image = self.texture[self.side][0]
        self.image.set_colorkey(BACKGROUND_COLOR)
        x, y = map_group.coord
        if self.rect.right > WIDTH:
            if map_group.can_coord_be((x, y + 1)):
                if self.rect.left > WIDTH:
                    self.rect.x = self.coord[0] = 0
                    map_group.coord = (x, y + 1)
            else:
                self.coord[0] = WIDTH - self.rect.width

        if self.rect.left < 0:
            if map_group.can_coord_be((x, y - 1)):
                if self.rect.right < 0:
                    self.rect.x = self.coord[0] = WIDTH - self.rect.width
                    map_group.coord = (x, y - 1)
            else:
                self.coord[0] = 0

        if self.rect.bottom > HEIGHT:
            if map_group.can_coord_be((x + 1, y)):
                if self.rect.top > HEIGHT:
                    self.rect.y = self.coord[1] = 0
                    map_group.coord = (x + 1, y)
            else:
                self.coord[1] = HEIGHT - self.rect.height

        if self.rect.top < 0:
            if map_group.can_coord_be((x - 1, y)):
                if self.rect.bottom < 0:
                    self.rect.y = self.coord[1] = HEIGHT - self.rect.height
                    map_group.coord = (x - 1, y)
            else:
                self.coord[1] = 0

        self.step = False

        # if pygame.sprite.spritecollide(self, game_obj.world.get_objects_draw(), False):
        #     for i in pygame.sprite.spritecollide(self, game_obj.world.get_objects_draw(), False):
        #         if isinstance(i, Item):
        #             self.inventory.addItem(i)
        #             self.world.objects[self.world.y][self.world.x].remove(i)
        #             game_obj.items_group.remove(i)

    def save_preload(self):
        self.texture = None
        self.image = None
        return self


class EventProcessor:
    def __init__(self):
        self.ded_flags = DedMoveFlags(False, False, False, False)
        self.running = True

    def process_events(self, events):
        for event in events:
            self._process_event(event)

    def _process_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.ded_flags.left = event.type == pygame.KEYDOWN
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.ded_flags.right = event.type == pygame.KEYDOWN
            if event.key in (pygame.K_UP, pygame.K_w):
                self.ded_flags.backward = event.type == pygame.KEYDOWN
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.ded_flags.forward = event.type == pygame.KEYDOWN


class SpriteStore:
    def __init__(self):
        self.ded_group = pygame.sprite.Group()
        self.nps_group = pygame.sprite.Group()
        self.item_group = pygame.sprite.Group()

    def add_ded(self, ded: Ded):
        self.ded_group.add(ded)

    def add_npc(self, npc: NPC):
        self.nps_group.add(npc)

    def add_item(self, item: Item):
        self.item_group.add(item)


def block_names_to_sprites(block_names_map):
    block_group = pygame.sprite.Group()
    for i, line in enumerate(block_names_map):
        for j, block_name in enumerate(line):
            block_group.add(TextureObject([j * BLOCK_SIZE, i * BLOCK_SIZE], block_name))
    return block_group


class MapStore:
    def __init__(self, maps_dir: str):
        self.maps_dir = maps_dir

    def load_maps(self, maps_group_name: str, start_coord=(0, 0)):
        maps_group_name = maps_group_name.replace('_', '-')
        return MapGroup(maps_group_name, start_coord)


class MapGroup:
    def __init__(self, map_name: str, start_coord: tuple[int, int]):
        self.__map_name = map_name
        self.__dict_map_coord = self.__create_map_dict()
        self.coord = list(start_coord)
        self.sprite_store = SpriteStore()
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
        for root, dirs, files in os.walk('maps'):
            for file in files:
                if file.startswith(self.__map_name) and file.endswith('.pickle'):
                    print('load map:', self.__map_name)
                    coord = tuple(map(int, file[:-7].split('_')[1:]))
                    block_names_map = self._load_map(os.path.join(root, file))
                    map_dict[coord] = block_names_to_sprites(block_names_map)
        return map_dict


class Game:
    def __init__(self):
        self.dialog = None
        self.init_game()
        self.game_loop()

    def init_game(self):
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.world = World(WORLD_MAP, *LOAD_DATA[1])
        self.map_store = MapStore('./')
        self.sprite_store = SpriteStore()
        self.map_group = self.map_store.load_maps('ded_home')
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 22)
        self.ded_init()

    def ded_init(self):
        self.ded = Ded(LOAD_DATA[0])
        self.sprite_store.add_ded(self.ded)

    # Обработка событий
    def game_loop(self):
        running = True
        event_processor = EventProcessor()
        while running:
            event_processor.process_events(pygame.event.get())
            running = event_processor.running
            ded_move_flags = event_processor.ded_flags
            self.ded.go_by_move_flags_object(ded_move_flags)

            current_map = self.map_group.get_current_map()

            self.sprite_store.ded_group.update(self.map_group)
            current_map.update()
            self.screen.fill(BLACK)
            current_map.draw(self.screen)
            self.sprite_store.ded_group.draw(self.screen)
            # for n in self.world.get_objects_draw():
            #     n.update()
            #     self.screen.blit(n.image, n.rect)

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    pygame.quit()

