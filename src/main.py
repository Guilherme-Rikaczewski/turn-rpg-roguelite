import pygame
from main_menu import MainMenu
from video_screen import VideoScreen
from enviroments import MAIN_MENU_BACKGROUND, INTRO_VIDEO

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

currrent_screen = "menu"

menu = MainMenu(screen)
menu.set_background(MAIN_MENU_BACKGROUND)

while running:

    click = False
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = True

    mouse_cursor = pygame.mouse.get_pos()

    match currrent_screen:
        case 'menu':
            menu.draw(mouse_cursor, click)

            if menu.finished:
                currrent_screen = 'intro'
        case 'intro':
            menu.video.draw()
            menu.chose_character()


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(30)  # limits FPS to 60

pygame.quit()
