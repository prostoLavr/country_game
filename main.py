import pygame
import os
import random
from PIL import Image

WIDTH = 720
HEIGHT = 480
FPS = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BACKGROUND_COLOR = (197, 30, 30)

DED_WIDTH = 50
DED_SPEED = 7
DED_STEP_SPEED = 3


class Block(pygame.sprite.Sprite):
    def __init__(self, coord, world_obj:World):
        pygame.sprite.Sprite.__init__(self)
        self.seed = random.randint(0, 4)
        #TODO: do something here



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
    def __init__(self):
        self.x = 0
        self.y = 0

    def right(self):
        self.x += 1
        print(self.x, self.y)

    def is_right(self):
        if self.x < 1:
            return True
        return False

    def left(self):
        self.x -= 1
        print(self.x, self.y)

    def is_left(self):
        if self.x > 0:
            return True
        return False

    def up(self):
        self.y += 1
        print(self.x, self.y)

    def is_up(self):
        if self.y < 1:
            return True
        return False

    def down(self):
        self.y -= 1
        print(self.x, self.y)

    def is_down(self):
        if self.y > 0:
            return True
        return False


class Person(pygame.sprite.Sprite):
    def __init__(self, coord, texture, world_obj:World):
        pygame.sprite.Sprite.__init__(self)
        self.now = 0
        self.texture = texture
        self.image = self.texture[0]
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.world = world_obj
        self.coord = coord
        self.step = False

    def go_forward(self, delta):
        self.coord[1] -= delta
        self.step = True

    def go_backward(self, delta):
        self.coord[1] += delta
        self.step = True

    def go_left(self, delta):
        self.coord[0] -= delta
        self.step = True

    def go_right(self, delta):
        self.coord[0] += delta
        self.step = True

    def update(self):
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]
        if self.step:
            self.now = (self.now + 1) % (len(self.texture) * DED_STEP_SPEED)
        else:
            self.now = 0
        self.image = self.texture[self.now // DED_STEP_SPEED]
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


class Game:
    def __init__(self):
        self.init_game()
        self.game_loop()

    def init_game(self):
        pygame.init()
        # pygame.mixer.init()  # Для звука
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()

        game_folder = os.path.dirname(__file__)
        img_folder = os.path.join(game_folder, 'img')
        ded_textures = []

        self.world = World()

        for i in ['ded.png', 'ded1.png', 'ded2.png']:
            resize_img = ResizeImg(os.path.join(img_folder, i), w=DED_WIDTH).get_filename()
            player_img = pygame.image.load(resize_img).convert()
            ded_textures.append(player_img)

        self.ded = Person([100, 100], ded_textures, self.world)
        self.all_sprites.add(self.ded)

        self.block

    def game_loop(self):
        left_flag = False
        right_flag = False
        forward_flag = False
        backward_flag = False
        running = True
        while running:
            self.all_sprites.update()
            self.screen.fill(WHITE)
            self.all_sprites.draw(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
                self.ded.go_forward(DED_SPEED)
            if backward_flag:
                self.ded.go_backward(DED_SPEED)

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    pygame.quit()
