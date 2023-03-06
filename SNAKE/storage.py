from elementary import Tile, Snake, Creature, SnakeTailElement
import my_globals

class ObjectsStorage:
    """
    Store all objects to exist in the game

    It can iterates over all the object stored for the purpose of collision detection
    """
    
    def __init__(self):
        self.tiles = []
        self.snake = []
        self.creatures = []
        self.__idx = 0
        self.__idy = 0

    def __dir__(self):
        return ["tiles", "snake", "creatures"]
    
    def __len__(self):
        return len(self.tiles) + len(self.snake) + len(self.creatures)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        while True:
            try:
                attr = dir(self)[self.__idx]
                try:
                    obj = getattr(self,attr)[self.__idy]
                except:
                    self.__idy = 0
                    self.__idx += 1 # iterates over attributes
                else:
                    self.__idy += 1 # iterates over attribute values
                    return obj
            except:
                self.__idx = 0
                raise StopIteration
            else:
                continue # prevents form putting None in the iterator
                         # when nested try fails and move to the next attribute

    def add(self, object):
        new_object_class = object.__class__.__name__
        new_object = object.__class__.__new__(object.__class__)
        # print(id(new_object))
        # print(new_object_class)
        
        if new_object_class == "Creature":   
            new_object.__init__(storage=self, number = len(self.creatures))
            self.creatures.append(new_object)
        elif new_object_class == "Snake":
            new_object.__init__(self, len(self.snake))
            self.snake.append(new_object)
        elif new_object_class == "SnakeTailElement":
            new_object.__init__(self, len(self.snake))
            self.snake.append(new_object)
        elif new_object_class == "Tile":
            new_object.__init__(self, len(self.tiles))
            self.tiles.append(new_object)

    def initialize(self, coordinates):
        for coordinate in coordinates:
            self.tiles.append(Tile(storage=self, number=len(self.tiles), position=coordinate))
        self.snake.append(Snake(self, len(self.snake)))

    def populate(self):
        while len(self.creatures) < my_globals.CREATURES_TO_BE:
            self.creatures.append(Creature(self, len(self.creatures)))

    def move(self, keyboard_input):
        self.snake_head.change_direction(keyboard_input)
        for object in self.snake:
            object.move()
        for object in self.creatures:
            object.move()


    @property
    def snake_head(self):
        return self.snake[0]
    

if __name__ == "__main__":

    

    print(__file__.__name__)