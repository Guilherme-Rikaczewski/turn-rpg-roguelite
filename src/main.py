import pygame
from main_menu import MainMenu
from enviroments import MAIN_MENU_BACKGROUND

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1353, 893))
clock = pygame.time.Clock()
running = True

menu = MainMenu(screen)
menu.set_background(MAIN_MENU_BACKGROUND)
menu.set_options


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_cursor = pygame.mouse.get_pos()

    # fill the screen with a color to wipe away anything from last frame
    menu.draw_background()
    menu.draw(mouse_cursor)

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
