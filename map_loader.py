import pickle
import os



class MapStore:
    def __init__(self, maps_dir: str)
        self.maps_dir = maps_dir

    def load_map(self, map_name: str):
        map_path = os.path.join(self.maps_dir, map_name)
        with open(map_path, 'rb') as map_file:
            map_list = pickle.load(map_file)
        return map_list
    
    def load_maps(self, maps_group_name: str, start_coord=(0, 0)):
        return MapGroup(maps_group_name, start_coord)


class MapsGroup:
    def __init__(self, map_name: str, start_coord: tuple[int, int]):
        self.coord = list(start_coord)
        self.__cached_coord = None
        self.__cached_map = None 

    def get_currnet_map(self):
        if self.__cached_coord != self.coord:
            map_path = os.path.join(self.maps_dir, map_name + '_'.join(self.coord))
            with open(map_path, 'rb') as map_file:
                map_list = pickle.load(map_file)
            return map_list
        else:
            return self.__cached_map
 
