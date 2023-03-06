import sys
import pygame
from random import randint, choice
from storage import ObjectsStorage
from maps import gen_coordinates
import my_globals

sys.path.append(__file__ + "\\..\\" )

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
        self.direction = choice([[1,0],[-1,0],[0,1],[0,-1]])
        self.speed = speed
        self.out = [False,False,False,False] # left top right bottom
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
                        # print(r"self.eat() should be called in .collision_check() cause i hit", object.__class__.__name__)
                    elif object.__class__ in reverse:
                        # print(r".collision_check() changes direction!")
                        self.reverse_direction()
                    elif object.__class__ in die:
                        if not hasattr(object, "first"): # strange things happen when reversed clause used
                            # self.die()
                            print(self.__class__.__name__, "says:")
                            print(r"self.die() should be called in .collision_check() cause i hit", object.__class__.__name__)
                    elif object.__class__ in ignore:
                        pass
                    else:
                        print("Type", object.__class__.__name__ ,
                            "not recognized by", self.__class__.__name__,
                            "during collision!")                  


#############################################################################################
## SNAKE - one-tile element to be controlled by a player

class Snake(Specimen):
    speed = my_globals.SPEED_SNAKE # class variable
    created = 0 # class counter

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

    def collision_check(self, objects: list):
        """
        Check collisions
        :param objects: list of objects to check on, check for self need to be done outside
        """
        eat = [Creature]
        reverse = []
        die = [Tile, SnakeTailElement]
        ignore = []

        super().collision_check(objects=objects, eat=eat, reverse=reverse, die=die, ignore=ignore)

    def move(self):
        super().move()
        self.collision_check(self.storage)

    
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
        self.collision_check(self.storage)
        if any(self.out):
            self.reverse_direction()
    
    def delete(self):
        print("deleting!")
        my_idx = self.storage.creatures.index(self)
        print("Disappears creature from cell", my_idx)
        del self.storage.creatures[my_idx]
        Creature.destroyed += 1

    def collision_check(self, objects: list):
        """
        Check collisions
        :param objects: list of objects to check on, check for self need to be done outside
        """
        eat = []
        reverse = [Tile, Creature, SnakeTailElement]
        die = [Snake]

        super().collision_check(objects=objects, eat=eat, reverse=reverse, die=die)

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


#############################################################################################
##  MODULE TESTING
#############################################################################################
if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((my_globals.WIDTH, my_globals.HEIGHT))
    back_color = (0,0,0)
    clock = pygame.time.Clock()
    font40 = pygame.font.SysFont(None, 40)
    runtime_seconds = 0

    frame_number = 0 # used to print diagnostics to the console

    storage = ObjectsStorage()
    map_elements = []
    for coordinate in gen_coordinates():
        map_elements.append(Tile(position=coordinate))
    storage.load_map(map_elements)

    # tiles = []
    # tiles.append(Tile())
    # tiles.append(Tile())
    # for tile in tiles:
    #     storage.add(tile)
    
    # snakes = []
    # snakes.append(Snake())
    # for snake in snakes:
    #     storage.add(snake)
    
    # creatures = []
    # creatures.append(Creature())
    storage.add(Tile())
    storage.add(Tile())
    storage.add(Snake())
    storage.add(Creature())

    

    key_input_latch = {"left": False,
                        "up": False,
                        "right": False,
                        "down": False}
    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        
        key_input = pygame.key.get_pressed()
        if any([key_input[pygame.K_LEFT],key_input[pygame.K_UP],key_input[pygame.K_RIGHT],key_input[pygame.K_DOWN]]):
            key_input_latch = {"left": key_input[pygame.K_LEFT],
                               "up": key_input[pygame.K_UP],
                               "right": key_input[pygame.K_RIGHT],
                               "down": key_input[pygame.K_DOWN]}

    # -------------------------------- CREATING ELEMENTS     ----------------------------- 
        runtime_seconds = pygame.time.get_ticks()//1000
        
        if Creature.created < runtime_seconds // Creature.spawn_period:
            storage.add(Creature())
        
    # -------------------------------- MOVING INTERACTIVE ELEMENTS -----------------------
        storage.snake_head.change_direction(key_input_latch)

        for creature in storage.creatures:
            creature.change_direction()
            creature.move()

        for snake in storage.snake:
            snake.move()


    # -------------------------------- REDRAWING THE SCREEN ------------------------------
        screen.fill(back_color)

        # texts goes first
        text = font40.render(f"Tiles: {len(storage.tiles)}", True, (0, 255, 0))
        screen.blit(text, (20, 20))
        text = font40.render(f"Snakes: {len(storage.snake)}", True, (0, 255, 0))
        screen.blit(text, (20, 60))
        text = font40.render(f"Creatures in-class {Creature.created}", True, (0, 255, 0))
        screen.blit(text, (20, 100))
        text = font40.render(f"Creatures in-store {len(storage.creatures)}", True, (0, 255, 0))
        screen.blit(text, (20, 140))
        text = font40.render(f"Seconds in-game {runtime_seconds}", True, (0, 255, 0))
        screen.blit(text, (20, 180))
        

        for object in storage:
            object.blit(screen)

        pygame.display.flip()

    # -------------------------------- FPS LOCK             ------------------------------ 
        clock.tick(my_globals.FPS_LOCK) 
    # -------------------------------- DIAGNOSTICS TO THE CONSOLE ------------------------ 
        frame_number += 1
        if frame_number//my_globals.FPS_LOCK == my_globals.DIAGNOSTICS_PRINT_SECONDS:
            frame_number = 0
            print("#" * 20)
            print("Seconds in game:", pygame.time.get_ticks()//1000)
            print("Elements in storage:", len(storage))
            # print("Tiles created:", Tile.created)
            # print("Specimens created:", Specimen.created)
            # print("Snakes created:", Snake.created)
            # print("Creatures created:", Creature.created)
            # print("SnailTailElements created:", SnakeTailElement.created)