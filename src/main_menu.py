from pygame import Surface, SRCALPHA, BLEND_RGBA_MULT, quit
from pygame.transform import smoothscale
from pygame.draw import rect
from pygame.rect import Rect
from pygame.font import Font
from pygame.mixer import Sound
from video_screen import VideoScreen
from pygame.mixer_music import set_volume, play, load, stop
from enviroments import (MAIN_MENU_FONT, MAIN_MENU_HOVER_SOUND, 
                         MAIN_MENU_CLICK_SOUND, MAIN_MENU_THEME)


class MainMenu():
    def __init__(self, screen):
        self.screen = screen
        self.options = None
        self.background = None
        self.border_color = (0, 0, 0, 0)
        self.hover_sound = Sound(MAIN_MENU_HOVER_SOUND)
        self.hover_state = [False, False, False]
        self.click_sound = Sound(MAIN_MENU_CLICK_SOUND)
        
        load(MAIN_MENU_THEME)
        set_volume(0.0)
        play(-1)

        self.music_volume = 0.0
        self.target_volume = 0.5
        self.fade_speed = 0.01

        # muda pra True quando clicar pra ir pra outra tela
        self.should_fade_out = False

        self.visual_alpha = 0        # 0 = visível, 255 = preto total
        self.visual_fading = False   # vira True quando clicar JOGAR
        self.visual_speed = 4        # velocidade do fade
        self.finished = False        # usado para avisar à main() que pode trocar de tela

        self.hide_options = False

        self.show_text = True
        self.intro_text = ['A viagem foi longa', 'Já está anoitecendo', 'É melhor descansar']
        self.intro_alpha = 0
        self.intro_fading = True
        self.intro_speed = 2

        self.intro = False
        self.frame_count = 0

    def set_background(self, path):
        self.background = VideoScreen(self.screen, path)

    def handle_click(self, text):

        match text:
            case 'JOGAR':
                # self.should_fade_out = True
                self.click_sound.play()
                self.hide_options = True
                self.intro = True
            case 'CONFIGURAR':
                self.should_fade_out = True
                self.click_sound.play()
            case 'SAIR':
                self.click_sound.play()
                quit()

    def init_intro(self):
        if not self.intro:
            return
        
        if not self.show_text:
            self.visual_fading = True
            return

        # --- SE A LISTA ACABOU, COMEÇA O FADE OUT --- #
        if not self.intro_text:  
            self.visual_fading = True
            return

        # Fonte
        font = Font(MAIN_MENU_FONT, 64)

        # Texto atual (sempre o primeiro da lista)
        current_text = self.intro_text[0]

        # Render do texto atual
        rendered = font.render(current_text, True, (255, 255, 255))
        text_rect = rendered.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2
            )
        )

        # Fade-in do texto
        if self.intro_fading:
            self.intro_alpha = min(self.intro_alpha + self.intro_speed, 255)
            
            if self.frame_count < 120:
                self.frame_count += 1
            if self.intro_alpha == 255 and self.frame_count == 120:
                self.frame_count = 0
                self.intro_fading = False  # fim do fade

        # Surface temporária
        temp_surface = Surface(rendered.get_size(), SRCALPHA)
        temp_surface.blit(rendered, (0, 0))

        # Aplica alpha gradual
        temp_surface.fill(
            (255, 255, 255, self.intro_alpha),
            special_flags=BLEND_RGBA_MULT
        )
        

        # Desenha texto
        self.screen.blit(temp_surface, text_rect)

        # Quando terminar o fade-in, troca para o próximo texto
        if not self.intro_fading:
            self.intro_text.pop(0)   # remove o primeiro texto

            # Se ainda tem texto → prepara próximo
            if self.intro_text:
                self.intro_alpha = 0
                self.intro_fading = True
            else:
                # acabou tudo → fade da tela
                self.visual_fading = True

    def update_visual_fade(self):
        if self.visual_fading:
            if self.visual_alpha < 255:
                self.visual_alpha = min(
                    self.visual_alpha + self.visual_speed, 255
                )

                fade_surface = Surface(self.screen.get_size(), SRCALPHA)
                fade_surface.fill((0, 0, 0, self.visual_alpha))
                self.screen.blit(fade_surface, (0, 0))

            else:
                # fade completo → troca a tela
                self.finished = True
                self.turn_black()

    def turn_black(self):
        surf = Surface(self.screen.get_size(), SRCALPHA)
        surf.fill((0, 0, 0, 255))
        self.screen.blit(
            surf,
            (0, 0)
        )

    def update_music(self):
        if not self.should_fade_out:
            if self.music_volume < self.target_volume:
                self.music_volume = min(
                    self.music_volume + self.fade_speed, self.target_volume
                )
                set_volume(self.music_volume)
        else:
            if self.music_volume > 0:
                self.music_volume = max(
                    self.music_volume - self.fade_speed, 0
                )
                set_volume(self.music_volume)
            else:
                stop()

    def draw_panel(self):
        width = 400
        height = 260
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

    def draw_options(self, mouse_pos, click):
        # mesmas posições do painel
        width = 400
        height = 280
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

        radius = 10

        for i, text in enumerate(self.options):
            bx = panel_x + 20
            by = start_y + (button_height + spacing) * i

            # retângulo do botão
            rect_surface = Surface((button_width, button_height), SRCALPHA)

            # fundo do botão
            option_rect = Rect(bx, by, button_width, button_height)
            
            is_hover = option_rect.collidepoint(mouse_pos)

            # som do hover
            if is_hover and not self.hover_state[i]:
                self.hover_sound.play()
            
            self.hover_state[i] = is_hover

            # clique na opção
            if is_hover and click:
                self.handle_click(text)

            self.border_color = (239, 153, 34, 255) if is_hover else (
                0, 0, 0, 0
                )
            
            rect(
                rect_surface,
                (0, 0, 0, 120),  # cor interna semi-transparente
                (0, 0, button_width, button_height),
                border_radius=radius
            )

            # borda
            rect(
                rect_surface,
                self.border_color,   # cor da borda
                (0, 0, button_width, button_height),
                width=2,
                border_radius=radius
            )

            # render texto
            rendered = font.render(text, True, (239, 153, 34))
            text_rect = rendered.get_rect(
                center=(button_width // 2, button_height // 2)
            )

            rect_surface.blit(rendered, text_rect)

            # desenhar o botão na tela
            self.screen.blit(rect_surface, (bx, by))

    def draw(self, mouse_pos, click):
        self.background.draw(fade=False)
        if not self.hide_options:
            self.draw_panel()
            self.draw_options(mouse_pos, click)
        self.update_music()
        self.init_intro()
        # self.update_visual_fade()
