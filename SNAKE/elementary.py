import my_globals
import pygame
from random import randint, choice
import inspect


#############################################################################################
##  CLASSES TO ELEMENTS
#############################################################################################
## Main class - Everything is a tile!
class Tile:
    created = 0 # class variable - counter
    destroyed = 0 # class variable - counter
    spawn_period = 1 # seconds

    def __init__(self, storage=None, number=None, img_path=None, size=my_globals.SIZE, color=(255,255,255,1), position=None):
        """
        :param img_path: path string to an image (must be a square)
        :param size: used when no img_path specified
        :param color: used when no img_path specified
        :param position: (x,y) in pixels for the top-left corner
        """
        if img_path==None:
            self.image = pygame.Surface((size, size))
            self.image.fill(color)  
        else:
            self.image = pygame.image.load(img_path)
        assert self.width == self.height, "The image provided is not a square."
        if position==None:
            self.position = self.image.get_rect().move(self.generate_coordinates())
        else:
            self.position = self.image.get_rect().move(position)
        self.storage = storage
        self.number = number

        

        if storage != None:
            __class__.created += 1

    def generate_coordinates(self, x=None, y=None):
        """
        Generate random coordinates on the grid of squares
        """
        x = (randint(0, my_globals.WIDTH//self.size - 1)) * self.size
        y = (randint(0, my_globals.HEIGHT//self.size - 1)) * self.size
        return (x,y)

    def blit(self, screen: pygame.Surface):
        screen.blit(self.image, self.position)
        # future implementation of no collision with screen borders
        # if self.position.top < 0:
        #     pass
        # if self.position.left < 0:
        #     pass
        # if self.position.right > screen.get_width():
        #     pass
        # if self.position.bottom > screen.get_height():
        #     pass

    def delete(self):
        del self
        Tile.destroyed += 1

    @property
    def width(self):
        return self.image.get_width()
    
    @property
    def height(self):
        return self.image.get_height()
    
    @property
    def size(self):
        return self.image.get_height()


#############################################################################################
## SPECIMEN - a superclass for everyting that moves

class Specimen(Tile):
    """
    Implements movement and collision detection.

    This an intermidate class that does not have existing instances in the game
    """
    created = 0

    def __init__(self, storage=None, number=None, img_path=None, color=(255,0,0,1), position=None, speed=1):
        """
        :param img_path: path string to an image (must be a square)
        :param size: used when no img_path specified
        :param color: used when no img_path specified
        :param position: (x,y) in pixels for the top-left corner
        :param speed: number of pixels Snake moves every frame
        """
        super().__init__(storage=storage,
                         number=number,
                         img_path=img_path,
                         color=color, 
                         position=position)
        while True and self.__class__.__name__ != "SnakeTailElement":
            # print(self.__class__.__name__)
            if any(self.position.colliderect(object.position) for object in self.storage if id(object) != id(self)):
                print("Readjustment while creating!")
                self.position.left, self.position.top = self.generate_coordinates()
            else:
                break
        self.direction = choice([[1,0],[-1,0],[0,1],[0,-1]])
        self.speed = speed
        self.out = [False,False,False,False] # left top right bottom

        # while self.collision_check:
        #     self.position.move((16,16))
        #     print("Position readjusted during creation!")
        if storage != None:
            __class__.created += 1

    def out_the_border(self) -> list:
        """
        Detect when Specimen went outside the screen.

        Helper function for Snake.move()
        :return: booleans for crossing [left top right bottom] borders
        """
        return [self.position.left < 0,
                self.position.top < 0, 
                self.position.right > my_globals.WIDTH,
                self.position.bottom > my_globals.HEIGHT]
    
    def move(self):
        """
        Move Specimen every frame depending on its .position
        """
        if self.direction[0]==1 : 
            self.position.left += self.speed
        if self.direction[0]==-1 : 
            self.position.left -= self.speed
        if self.direction[1]==1 : 
            self.position.top += self.speed
        if self.direction[1]==-1 : 
            self.position.top -= self.speed
        self.out = self.out_the_border()
        self.collision_check(self.storage)

    def grid_fit(self):
        """
        Return True if topleft corner position fits the grid.

        Helper function for .change_direction() as children's method
        """
        return not (self.position.left % self.size or self.position.top % self.size)
    
    def reverse_direction(self):
        self.direction[0] *= -1
        self.direction[1] *= -1
    
    def collision_check(self, objects: list, eat=[], reverse=[], die=[], ignore=[]):
        """
        Check if the object collides with any object provided in the list.

        Further action depends on type of the object it collides with
        :param objects: objects to check on
        :param eat: edibles
        :param reverse: bounce back
        :param die: killers
        """
        if len(objects) == 0:
            return
        
        for object in objects:
            if id(object) != id(self):
                if self.position.colliderect(object.position):
                    if object.__class__ in eat:
                        self.eat(object)
                    elif object.__class__ in reverse:
                        self.reverse_direction()
                    elif object.__class__ in die:
                        if not hasattr(object, "first"): # strange things happen when reversed clause used
                            self.die()
                    elif object.__class__ in ignore:
                        pass
                    else:
                        print("Type", object.__class__.__name__ ,
                            "not recognized by", self.__class__.__name__,
                            "during collision!")
                    return True                  


#############################################################################################
## SNAKE - one-tile element to be controlled by a player

class Snake(Specimen):
    speed = my_globals.SPEED_SNAKE # class variable
    created = 0 # class counter
    reason = None # reason of death to be set in .die() method

    def __init__(self, storage=None, number=None, img_path=None, color=(255,0,0,1), position=None, speed=speed):
        super().__init__(storage=storage, number=number, color=color, speed=speed, img_path=img_path)
        self.eaten = 0 # counter
        self.live = True
        __class__.created += 1
    
    def change_direction(self, key_input_latch: dict):
        """
        :param key_input_latch: a dictionary of latched arrows input (last time any of them was True)
        """          
        if key_input_latch["left"] and self.grid_fit() and self.direction != [1,0]: 
            self.direction = [-1,0] 
        if key_input_latch["up"] and self.grid_fit() and self.direction != [0,1]: 
            self.direction = [0,-1]
        if key_input_latch["right"] and self.grid_fit() and self.direction != [-1,0]: 
            self.direction = [1,0]  
        if key_input_latch["down"] and self.grid_fit() and self.direction != [0,-1]: 
            self.direction = [0,1] 

    def eat(self, object_eaten):
        self.eaten += 1
        object_eaten.delete()
        self.storage.add(SnakeTailElement())

    def die(self):
        __class__.reason = inspect.stack()[1][3]
        self.live = False

    def collision_check(self, objects: list):
        """
        Check collisions
        :param objects: list of objects to check on, check for self need to be done outside
        """
        eat = [Creature]
        reverse = []
        die = [Tile, SnakeTailElement]
        ignore = []

        return super().collision_check(objects=objects, eat=eat, reverse=reverse, die=die, ignore=ignore)

    def move(self):
        super().move()
        if any(self.out):
            self.die()
        # self.collision_check(self.storage)

    
#############################################################################################
## CREATURE - one-tile element to exist on its own and to serve as a prey

class Creature(Specimen):
    created = 0 # class counter
    destroyed = 0 # class variable - counter
    spawn_period = my_globals.CREATURE_SPAWN # seconds

    chance_to_turn = 10 # percent
    turns_taken = 0 # class variable - counter
    speed = my_globals.SPEED_CREATURE # class variable
    
    def __init__(self, storage=None, number=None, img_path=None, color=(0,0,255,1), speed=speed):
        super().__init__(storage=storage, number=number, color=color, speed=speed, img_path=img_path)
        self.turn_flag = False
        if storage != None:
            __class__.created += 1

    def change_direction(self):
        """
        Creatures turns automatically at random
        """
        if self.grid_fit():
            if randint(1,100) <= Creature.chance_to_turn:
                self.turn_flag = True
        if self.turn_flag:
            self.turn_flag = False
            choices = [[1,0],[-1,0],[0,1],[0,-1]]
            choices.remove(self.direction)
            self.direction = choice(choices)
            Creature.turns_taken += 1
    
    def move(self):
        super().move()
        if any(self.out):
            self.reverse_direction()
    
    def delete(self):
        # print("deleting!")
        my_idx = self.storage.creatures.index(self)
        # print("Disappears creature from cell", my_idx)
        del self.storage.creatures[my_idx]
        Creature.destroyed += 1

    def collision_check(self, objects: list):
        """
        Check collisions
        :param objects: list of objects to check on, check for self need to be done outside
        """
        eat = []
        reverse = [Tile, Creature, SnakeTailElement]
        die = []
        ignore = [Snake]

        return super().collision_check(objects=objects, eat=eat, reverse=reverse, die=die, ignore=ignore)

#############################################################################################
## SNAKE TAIL ELEMENT

class SnakeTailElement(Snake):
    """Tiles to follow Snake's head and be created any time it eats a Creature"""
    created = 0
    speed = my_globals.SPEED_SNAKE

    def __init__(self, storage=None, number=None, img_path=None, color=(255,0,0,1), position=None, speed=speed):
        """
        That one will be tricky
        """
        super().__init__(storage=storage, number=number, color=color, speed=speed, img_path=img_path)
        
        self.lag = my_globals.SIZE//self.speed
        self.positions = []
        if storage != None:
            self.position = pygame.Rect(self.storage.snake[self.number-1].position)
            for i in range(self.lag):
                self.positions.append(pygame.Rect(self.storage.snake[self.number-1].position))
            if self.number == 1:
                self.first = True # used for no collision only
            __class__.created += 1

    def move(self):
        self.position = self.positions.pop()
        self.positions.insert(0, pygame.Rect(self.storage.snake[self.number-1].position))