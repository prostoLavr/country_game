import pygame
import os
from PIL import Image


WIDTH = 360
HEIGHT = 480
FPS = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DED_WIDTH = 50
DED_SPEED = 5

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


class Person(pygame.sprite.Sprite):
    def __init__(self, coords, texture):
        pygame.sprite.Sprite.__init__(self)
        self.now = 0
        self.texture = texture
        self.image = self.texture[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.coords = coords
        self.step = False


    def go_forward(self, delta):
        self.coords[1] -= delta
        self.step = True

    def go_backward(self, delta):
        self.coords[1] += delta
        self.step = True

    def go_left(self, delta):
        self.coords[0] -= delta
        self.step = True

    def go_right(self, delta):
        self.coords[0] += delta
        self.step = True


    def update(self):
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]
        if self.step:
            self.now = (self.now + 1) % len(self.texture)
            self.image = self.texture[self.now]
        self.step = False


def game_loop():
    left_flag = False
    right_flag = False
    forward_flag = False
    backward_flag = False
    running = True
    while running:
        all_sprites.update()
        screen.fill(BLACK)
        all_sprites.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    left_flag = True
                if event.key == pygame.K_w:
                    forward_flag = True
                if event.key == pygame.K_s:
                    backward_flag = True
                if event.key == pygame.K_d:
                    right_flag = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    left_flag = False
                if event.key == pygame.K_w:
                    forward_flag = False
                if event.key == pygame.K_s:
                    backward_flag = False
                if event.key == pygame.K_d:
                    right_flag = False
        if left_flag:
            ded.go_left(DED_SPEED)
        if right_flag:
            ded.go_right(DED_SPEED)
        if forward_flag:
            ded.go_forward(DED_SPEED)
        if backward_flag:
            ded.go_backward(DED_SPEED)

        pygame.display.flip()
        clock.tick(FPS)

pygame.init()
# pygame.mixer.init()  # Для звука
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
screen.fill(WHITE)
all_sprites = pygame.sprite.Group()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
ded_textures = []

resize_img = ResizeImg(os.path.join(img_folder, 'ded.png'), DED_WIDTH).get_filename()
player_img = pygame.image.load(resize_img).convert()
ded_textures.append(player_img)
resize_img = ResizeImg(os.path.join(img_folder, 'ded1.png'), DED_WIDTH).get_filename()
player_img = pygame.image.load(resize_img).convert()
ded_textures.append(player_img)


ded = Person([0, 0], ded_textures)
all_sprites.add(ded)


if __name__ == '__main__':
    game_loop()
    pygame.quit()
