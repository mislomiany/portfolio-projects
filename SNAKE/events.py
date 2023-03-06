import pygame
import sys
from time import strftime


arrows = {"left": False,
          "up": False,
           "right": False,
           "down": False}


def handle_events():
    for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()


def arrows_latch():
    global arrows
    key_input = pygame.key.get_pressed()

    if any([key_input[pygame.K_LEFT],key_input[pygame.K_UP],key_input[pygame.K_RIGHT],key_input[pygame.K_DOWN]]):
        arrows = {"left": key_input[pygame.K_LEFT],
                            "up": key_input[pygame.K_UP],
                            "right": key_input[pygame.K_RIGHT],
                            "down": key_input[pygame.K_DOWN]}


def arrows_initialize():
     return {"left": False,
                "up": False,
                "right": False,
                "down": False}


def print_diagnostics(storage):
    print("### CREATURES POSITION:")
    for creature in storage.creatures:
        print(creature.position.topleft,end=";")
    else:
        print("\n\n")


def game_over_dump(storage, timer):
    timer //= 1000000000 # conversion from nano to seconds
    file_path = __file__ + "\\..\\logs\\"
    map_name = "log"
    with open(file_path + map_name + ".txt", "a", encoding="utf-8") as log_file:
         print(f'{strftime("%d %b %Y %H:%M:%S +0000")}:\n\
               \tEaten: {storage.snake_head.eaten}\n\
               \tTime in game: {timer//60}min {timer%60}s\n\
               \tDead by: {storage.snake_head.reason}', file=log_file)
    print("Logs stored!")