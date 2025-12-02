from pygame.image import load
from pygame.surface import Surface
from abc import ABC, abstractmethod


class Menu(ABC):
    def __init__(self, screen: Surface):
        self.screen: Surface = screen
        self.options: list | None = None
        self.background = None

    def set_background(self, path):
        self.background = load(path)

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))

    def set_options(self, options: list):
        self.options = options

    @abstractmethod
    def draw_options(self):
        pass

    @abstractmethod
    def draw(self):
        pass