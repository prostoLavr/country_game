from dataclasses import dataclass

import pygame


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

BACKGROUND_COLOR = (204, 51, 51)

OPEN_SAVE = False
FILE_SAVE = '../save'


@dataclass
class DedMoveFlags:
    left: bool
    right: bool
    forward: bool
    backward: bool


@dataclass
class MoveSide:
    FORWARD = 0
    BACKWARD = 1
    RIGHT = 2
    LEFT = 3
