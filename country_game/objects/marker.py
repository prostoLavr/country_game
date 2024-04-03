from country_game.texture_loadger import TextureLoader

texture_loader = TextureLoader()


class Marker(pygame.sprite.Sprite):
    WIDTH = 50

    def __init__(self, coordinates):
        super().__init__()
        self.image = texture_loadger.get_texture('marker')
        self.image.set_colorkey(config.BACKGROUND_COLOR)
        self.rect = self.image.get_rect()

