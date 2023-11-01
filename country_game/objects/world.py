from country_game import config


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
                            up_obj_map_list.append(
                                House(
                                    [j * config.BLOCK_SIZE,
                                     i * config.BLOCK_SIZE]
                                )
                            )
                        else:
                            tmp_lst.append(
                                TextureObject(
                                    [j * config.BLOCK_SIZE,
                                     i * config.BLOCK_SIZE],
                                    str(obj_str)
                                )
                            )
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

