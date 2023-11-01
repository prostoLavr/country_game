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
        self.image.set_colorkey(config.BACKGROUND_COLOR)
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
                            ret['answers'] = [
                                {'text': ans.text, 'to': ans.attrib['to']} for
                                ans in list(p)[1]]
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
                self.now = (self.now + 1) % ((len(
                    self.texture[self.side][1:]
                )) * Ded.DED_STEP_SPEED)
                self.image = self.texture[self.side][1:][
                    self.now // Ded.DED_STEP_SPEED]
            else:
                self.now = 0
                self.image = self.texture[self.side][0]
            self.image.set_colorkey(config.BACKGROUND_COLOR)
            self.step = False

            if self.point_move:
                if self.rect.x not in range(
                        self.point_move[0] - NPC.SPEED,
                        self.point_move[0] + NPC.SPEED
                ) \
                        and self.point_move[0] > self.rect.x:
                    self.move(RIGHT)
                elif self.rect.x not in range(
                        self.point_move[0] - NPC.SPEED,
                        self.point_move[0] + NPC.SPEED
                ) \
                        and self.point_move[0] < self.rect.x:
                    self.move(LEFT)
                elif self.rect.y not in range(
                        self.point_move[1] - NPC.SPEED,
                        self.point_move[1] + NPC.SPEED
                ) \
                        and self.point_move[1] < self.rect.y:
                    self.move(FORWARD)
                elif self.rect.y not in range(
                        self.point_move[1] - NPC.SPEED,
                        self.point_move[1] + NPC.SPEED
                ) \
                        and self.point_move[1] > self.rect.y:
                    self.move(BACKWARD)
                else:
                    self.point_move = None
            else:
                self.point_move = (random.randrange(
                    0, config.WIDTH - self.image.get_size()[0], NPC.SPEED
                ),
                                   random.randrange(
                                       0,
                                       config.HEIGHT - self.image.get_size()[1],
                                       NPC.SPEED
                                   ))

