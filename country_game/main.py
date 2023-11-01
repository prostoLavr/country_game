import pickle
from enum import Enum

import pygame

from country_game import config
from country_game.objects.ded import Ded
from country_game.texture_loadger import TextureLoader
from country_game import stores
from config import DedMoveFlags


if config.OPEN_SAVE:
    with open(config.FILE_SAVE, 'rb') as file:
        LOAD_DATA = pickle.load(file)
else:
    LOAD_DATA = [100, 100], (0, 0)

texture_loader = TextureLoader()


class EventProcessStatus(Enum):
    NOTHING = 0
    EXIT = 1


class House(pygame.sprite.Sprite):
    def __init__(self, coord):
        pygame.sprite.Sprite.__init__(self)
        self.coord = coord
        self.image = texture_loader.get_textures('house', 150)[0]
        self.set_rect_and_coord()

    def set_rect_and_coord(self):
        self.rect = self.image.get_rect()
        self.rect.center = (config.WIDTH / 2, config.HEIGHT / 2)
        self.rect.x = self.coord[0]
        self.rect.y = self.coord[1]


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


class Game:
    def __init__(self):
        self.dialog = None
        self.init_game()
        self.game_loop()

    def init_game(self):
        pygame.font.init()
        self.screen = pygame.display.set_mode(
            (config.WIDTH, config.HEIGHT), pygame.FULLSCREEN
        )
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.map_store = stores.MapStore('../')
        self.sprite_store = stores.SpriteStore()
        self.map_group = self.map_store.load_maps('start')
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
            self.screen.fill(config.BLACK)
            current_map.draw(self.screen)
            self.sprite_store.ded_group.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(config.FPS)


def main():
    game = Game()
    pygame.quit()


if __name__ == '__main__':
    main()
