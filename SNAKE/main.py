import window
import events
import storage
import my_globals
import time
import sys

objects = storage.ObjectsStorage()
objects.initialize(window.coordinates)

events.arrows_initialize()
main_start = time.time_ns()

while True:
    start = time.time_ns()
    events.handle_events()
    events.arrows_latch()


    objects.populate()
    objects.move(events.arrows)

    # events.print_diagnostics(objects)
    # print("Is he alive:", objects.snake_head.live)
    info_string = f"Elements: {len(objects)}   Creatures: {len(objects.creatures)}   Eaten: {objects.snake_head.eaten}"
    if objects.snake_head.live:
        info = window.refresh_info(info_string)
        window.refresh_screen(window.screen, info, objects)
    elif not window.game_over_displayed:
        main_end = time.time_ns()
        info = window.refresh_info(info_string)
        window.game_over_displayed = window.game_over_screen(window.screen, info, objects)
        events.game_over_dump(objects, timer=main_end-main_start)
        time.sleep(1)
        sys.exit()
    stop = time.time_ns()
    if stop-start > 5000000:
        print("Time in loop:", stop-start)

    window.clock.tick(my_globals.FPS_LOCK) 
    