import pygame
import maps
import time
import events
# import vars

BLACK = (0,0,0,1)
WHITE = (255,255,255,1)
COLOR = (255,255,0,1)
INFO_HEIGHT = 50
INFO_PADDING = 10

game_size, coordinates = maps.load_map("map")

map_width, map_height = game_size
info_width, info_height = map_width, INFO_HEIGHT


pygame.init()
screen = pygame.display.set_mode((map_width, map_height + info_height))

clock = pygame.time.Clock()
game_over_displayed = False


def refresh_info(text):
    info_font = pygame.font.SysFont(None, INFO_HEIGHT - 2*INFO_PADDING)
    info_text = info_font.render(text, True, WHITE)
    info_surf = pygame.Surface((info_width, info_height))
    pygame.draw.line(info_surf, WHITE, (0,0), (info_width,0))
    info_surf.blit(info_text, (INFO_PADDING, 1.5*INFO_PADDING))
    return info_surf

def print_map(screen, info, objects):
    screen.fill(BLACK)
    screen.blit(info, (0, map_height))
    for tile in objects.tiles: 
        tile.blit(screen)
    return screen


def refresh_screen(screen, info, objects):
    # screen.fill(BLACK)
    # screen.blit(info, (0, map_height))
    # seems like iterating over separate lists prevents screen flickering
    # and give better control what to display first
    # for tile in objects.tiles: 
        # tile.blit(screen)
    screen = print_map(screen, info, objects)

    for creature in objects.creatures:
        creature.blit(screen)
    for snake in objects.snake:
        snake.blit(screen)
    pygame.display.flip()

def game_over_screen(screen, info, objects):
    info_font = pygame.font.SysFont(None, 100)
    text = info_font.render("GAME OVER", True, COLOR)

    frozen_filled = pygame.Surface.copy(screen)
    frozen_filled_text = pygame.Surface.copy(frozen_filled)
    frozen_filled_text.blit(text, (100,100))

    # screen = print_map(screen, info, objects)
    # frozen_empty = pygame.Surface.copy(screen)
    
    repetitions = 2

    i=0

    while i < repetitions:
        screen.fill(BLACK)
        screen.blit(frozen_filled_text, (0,0))
        pygame.display.flip()
        time.sleep(1)
        screen.fill(BLACK)
        screen.blit(frozen_filled, (0,0))
        pygame.display.flip()
        time.sleep(1)
        i += 1
    else:
        screen.fill(BLACK)
        screen.blit(frozen_filled_text, (0,0))
        pygame.display.flip()
        return True



    info_font = pygame.font.SysFont(None, 100)
    text = info_font.render("GAME OVER", True, COLOR)
    while True:
        events.handle_events()
        screen.blit(text, (100,100))
        pygame.display.flip()
        time.sleep(2)
        screen.fill(BLACK)
        screen.blit(frozen, (0,0))
        pygame.display.flip()
        time.sleep(2)


