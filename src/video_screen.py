import cv2
import pygame
from pygame import Surface, SRCALPHA


class VideoScreen:
    def __init__(self, screen, video_path):
        self.screen = screen
        self.cap = cv2.VideoCapture(video_path)

        self.width = screen.get_width()
        self.height = screen.get_height()

        self.finished = False

        self.visual_alpha = 255        # 0 = visível, 255 = preto total
        self.visual_fading = True   # vira True quando clicar JOGAR
        self.visual_speed = 4

    def update_visual_fade(self):
        if self.visual_fading:
            if self.visual_alpha <= 255:
                self.visual_alpha = max(
                    self.visual_alpha - self.visual_speed, 0
                )

                fade_surface = Surface(self.screen.get_size(), SRCALPHA)
                fade_surface.fill((0, 0, 0, self.visual_alpha))
                self.screen.blit(fade_surface, (0, 0))
            else:
                self.visual_fading = False

    def update(self):
        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height))

        surf = pygame.image.frombuffer(
            frame.tobytes(), (self.width, self.height), "RGB"
        )

        self.screen.blit(surf, (0, 0))

    def draw(self):
        self.update()
        self.update_visual_fade()

