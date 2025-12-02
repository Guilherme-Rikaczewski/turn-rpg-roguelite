from menu import Menu
from pygame import Surface, SRCALPHA, BLEND_RGBA_MULT
from pygame.transform import smoothscale
from pygame.draw import rect
from pygame.rect import Rect
from pygame.font import Font
from enviroments import MAIN_MENU_FONT


class MainMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.hover_color = (0, 0, 0, 0)

    def draw_panel(self):
        width = 400
        height = 400
        panel_x = 30
        panel_y = self.screen.get_height() - height - 30

        # 1) captura e garante per-pixel alpha
        background_area = self.screen.subsurface((panel_x, panel_y, width, height)).copy()
        background_area = background_area.convert_alpha()  # garante alpha por pixel

        # 2) blur multi-pass
        scale = 0.25
        blurred = background_area
        for _ in range(4):
            small = smoothscale(blurred, (max(1, int(width * scale)), max(1, int(height * scale))))
            blurred = smoothscale(small, (width, height)).convert_alpha()

        # 3) cria máscara arredondada (branca onde mantém, transparente onde corta)
        radius = 15
        mask = Surface((width, height), SRCALPHA)
        mask.fill((0, 0, 0, 0))
        rect(mask, (127, 15, 14, 235), (0, 0, width, height), border_radius=radius)

        # 4) cria surface final com alpha, blita o blur e aplica a máscara com MULT
        final = Surface((width, height), SRCALPHA)
        final.blit(blurred, (0, 0))                    # coloca o blur no final
        final.blit(mask, (0, 0), special_flags=BLEND_RGBA_MULT)  # corta com a máscara

        # 5) overlay arredondado (mesmo raio)
        overlay = Surface((width, height), SRCALPHA)
        overlay.fill((0, 0, 0, 0))
        rect(overlay, (0, 0, 0, 90), (0, 0, width, height), border_radius=radius)

        # 6) desenha tudo na tela
        self.screen.blit(final, (panel_x, panel_y))
        self.screen.blit(overlay, (panel_x, panel_y))

        # opcional: desenhar borda arredondada (stroke) por cima
        stroke_color = (239, 153, 34, 255)
        rect(self.screen, stroke_color,
                        (panel_x, panel_y, width, height),
                        width=3, border_radius=radius)

    def draw_options(self, mouse_pos):
        # mesmas posições do painel
        width = 400
        height = 400
        panel_x = 30
        panel_y = self.screen.get_height() - height - 30

        self.options = ["JOGAR", "CONFIGURAR", "SAIR"]

        # fonte (você pode ajustar tamanho e tipo)
        font = Font(MAIN_MENU_FONT, 48)

        button_width = width - 40     # margem interna de 20px
        button_height = 60
        spacing = 20

        # calculo posição inicial (para começar no topo do painel)
        start_y = panel_y + 40

        radius = 12

        for i, text in enumerate(self.options):
            bx = panel_x + 20
            by = start_y + (button_height + spacing) * i

            # retângulo do botão
            rect_surface = Surface((button_width, button_height), SRCALPHA)

            # fundo do botão
            option_rect = Rect(bx, by, button_width, button_height)
            
            is_hover = option_rect.collidepoint(mouse_pos)

            self.hover_color = (239, 153, 34, 255) if is_hover else (0, 0, 0, 0)
            
            rect(
                rect_surface,
                (0, 0, 0, 120),  # cor interna semi-transparente
                (0, 0, button_width, button_height),
                border_radius=radius
            )

            # borda
            rect(
                rect_surface,
                self.hover_color,   # cor da borda
                (0, 0, button_width, button_height),
                width=2,
                border_radius=radius
            )

            # render texto
            rendered = font.render(text, True, (239, 153, 34,))
            text_rect = rendered.get_rect(
                center=(button_width // 2, button_height // 2)
            )

            rect_surface.blit(rendered, text_rect)

            # desenhar o botão na tela
            self.screen.blit(rect_surface, (bx, by))

    def draw(self, mouse_pos):
        self.draw_panel()
        self.draw_options(mouse_pos)
