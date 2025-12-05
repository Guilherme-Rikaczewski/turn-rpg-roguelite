import pygame
from main_menu import MainMenu
from video_screen import VideoScreen
from enviroments import MAIN_MENU_BACKGROUND, INTRO_VIDEO

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1353, 893))
clock = pygame.time.Clock()
running = True

currrent_screen = "menu"

menu = MainMenu(screen)
menu.set_background(MAIN_MENU_BACKGROUND)

video: VideoScreen = None

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
            menu.draw_background()
            menu.draw(mouse_cursor, click)

            if menu.finished:
                menu.turn_black()
                video = VideoScreen(screen, INTRO_VIDEO)
                currrent_screen = 'video'
        case 'video':
            video.draw()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
