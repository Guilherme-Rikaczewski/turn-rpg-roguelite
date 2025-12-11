from pygame import Surface, SRCALPHA, BLEND_RGBA_MULT, quit
from pygame.transform import smoothscale
from pygame.draw import rect
from pygame.rect import Rect
from pygame.font import Font
from pygame.mixer import Sound
from video_screen import VideoScreen
from pygame.mixer_music import set_volume, play, load, stop
from enviroments import (MAIN_MENU_FONT, MAIN_MENU_HOVER_SOUND, 
                         MAIN_MENU_CLICK_SOUND, MAIN_MENU_THEME,
                         INTRO_VIDEO)


class MainMenu():
    def __init__(self, screen):
        self.screen = screen

        self.video = VideoScreen(screen, INTRO_VIDEO)

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

        # self.intro_text = ['A viagem foi longa', 'Já está anoitecendo', 'É melhor descansar']
        self.intro_text = []  # versao para teste mais rapido
        self.intro_alpha = 0
        self.intro_fading = True
        self.intro_speed = 2

        self.intro = False
        self.frame_count = 0

        self.chose_on = False
        self.chose_alpha = 0
        self.chose_fading = True
        self.chose_speed = 2

        self.chose_y_offset = 0        # posição inicial (0 = centro)
        self.chose_slide = False       # começa a deslizar?
        self.chose_slide_speed = 32     # velocidade base

        self.panel_y_offset = 100   # começa 200px abaixo da posição final
        self.panel_target_offset = -1000  # ponto final da animação
        self.panel_slide_speed = 32
        self.panel_sliding = False   # só começa quando você quiser



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
                # self.should_fade_out = True
                self.click_sound.play()
            case 'SAIR':
                self.click_sound.play()
                quit()

    def init_intro(self):
        if not self.intro:
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
                # self.should_fade_out = True

    def chose_character(self):
        if not self.chose_on:
            return

        font = Font(MAIN_MENU_FONT, 64)
        text = "Quem está dormindo?"

        rendered = font.render(text, True, (255, 255, 255))

        # posição do centro da tela + offset animado
        base_x = self.screen.get_width() // 2
        base_y = self.screen.get_height() // 2 + self.chose_y_offset

        text_rect = rendered.get_rect(center=(base_x, base_y))

        # --- FADE-IN DO TEXTO --- #
        if not self.chose_slide:   # fade só antes de deslizar
            if self.chose_fading:
                self.chose_alpha = min(self.chose_alpha + self.chose_speed, 255)

                if self.frame_count < 30:    # ~2s a 30fps
                    self.frame_count += 1

                if self.chose_alpha == 255 and self.frame_count == 30:
                    self.frame_count = 0
                    self.chose_fading = False
                    self.chose_slide = True   # começa a deslizar

        # --- ANIMAÇÃO DE DESLIZAR PARA CIMA --- #
        if self.chose_slide:
            # easing-out suave
            # OBS: não zere a velocidade imediatamente — deixe o easing diminuir
            self.chose_y_offset -= self.chose_slide_speed
            self.chose_slide_speed *= 0.92   # velocidade diminui com o tempo

            # quando a velocidade cair abaixo do gatilho, inicia a animação do painel
            # (isso evita chamar show_character() a cada frame e garante que o painel inicie só uma vez)
            if self.chose_slide_speed < 11:
                # inicia o slide do painel
                self.show_panel(
                    panel_id="painel1",
                    final_x=30,
                    final_y=100,
                    width=400,
                    height=200,
                    start_speed=80,
                    start_offset=0
                )
                # self.panel_sliding = True
                # opcional: resetar offsets/velocidade caso queira comportamento consistente
                # self.panel_y_offset = 200
                # self.panel_slide_speed = 20
            
            if self.chose_slide_speed < 10:
                self.show_panel(
                    panel_id="painel2",
                    final_x=450,
                    final_y=100,
                    width=400,
                    height=200,
                    start_speed=80,  # 18 de velocidade de diferença
                    start_offset=0
                )

            if self.chose_slide_speed < 9:
                self.show_panel(
                    panel_id="painel3",
                    final_x=30,
                    final_y=350,
                    width=400,
                    height=200,
                    start_speed=62,  # 18 de velocidade de diferença
                    start_offset=0
                )

            if self.chose_slide_speed < 8:
                self.show_panel(
                    panel_id="painel4",
                    final_x=450,
                    final_y=350,
                    width=400,
                    height=200,
                    start_speed=62,  # 18 de velocidade de diferença
                    start_offset=0
                )

            if self.chose_slide_speed < 7:
                self.show_panel(
                    panel_id="painel5",
                    final_x=30,
                    final_y=350,
                    width=400,
                    height=200,
                    start_speed=44,
                    start_offset=0
                )

            if self.chose_slide_speed < 6:
                self.show_panel(
                    panel_id="painel6",
                    final_x=450,
                    final_y=350,
                    width=400,
                    height=200,
                    start_speed=44,
                    start_offset=0
                )

            # evita vel neg/bug
            if self.chose_slide_speed < 0.5:
                self.chose_slide_speed = 0

        # --- APLICA O ALPHA --- #
        temp = Surface(rendered.get_size(), SRCALPHA)
        temp.blit(rendered, (0, 0))

        temp.fill((255, 255, 255, self.chose_alpha), special_flags=BLEND_RGBA_MULT)

        self.screen.blit(temp, text_rect)

        # se o painel já iniciou sliding, desenha-o também aqui (ou você pode desenhar em outro lugar)
        # chamar aqui garante ordem: texto (acima) e painel (abaixo) chegando do chão

    def show_panel(self, panel_id, final_x, final_y, width, height,
               start_speed=32, start_offset=0, radius=15):
        """
        Painel com animação 'liquid glass' vindo de fora da tela (por baixo).

        panel_id     → nome único do painel
        final_x/y    → posição final do painel
        width/height → tamanho do painel
        start_speed  → velocidade inicial do slide
        start_offset → distância EXTRA abaixo da borda inferior da tela para ele começar
        radius       → bordas arredondadas
        """

        screen_w, screen_h = self.screen.get_size()

        # Se não existe dict de estados, cria
        if not hasattr(self, "panel_states"):
            self.panel_states = {}

        # posição inicial REAL: fora da tela + offset adicional
        start_y = (screen_h + height) + start_offset

        # cria estado para esse painel se ele ainda não existe
        if panel_id not in self.panel_states:
            self.panel_states[panel_id] = {
                "y": start_y,
                "speed": start_speed,
                "sliding": True,
                "done": False
            }

        p = self.panel_states[panel_id]

        # ======================
        #   ANIMAÇÃO EASING OUT
        # ======================
        if p["sliding"]:
            p["y"] -= p["speed"]
            p["speed"] *= 0.92  # easing-out

            if p["y"] <= final_y:
                p["y"] = final_y
                p["speed"] = 0
                p["sliding"] = False
                p["done"] = True

        panel_y = p["y"]

        # Se ainda está fora da tela, não desenha
        if panel_y > screen_h:
            return

        # ======================
        #     RECORTE DE FUNDO
        # ======================
        vis_x = final_x
        vis_y = max(panel_y, 0)
        vis_h = min(panel_y + height, screen_h) - vis_y

        if vis_h <= 0:
            return

        try:
            background_area = self.screen.subsurface((vis_x, vis_y, width, vis_h)).copy().convert_alpha()
        except ValueError:
            return

        # se o painel está parcialmente fora da tela, preenche o restante
        if vis_h != height:
            tmp_full = Surface((width, height), SRCALPHA)
            tmp_full.fill((0, 0, 0, 0))

            # cola no topo ou no bottom dependendo de onde cortou
            dest_y = 0 if panel_y < 0 else height - vis_h

            scaled = smoothscale(background_area, (width, vis_h)).convert_alpha()
            tmp_full.blit(scaled, (0, dest_y))
            background_area = tmp_full

        # ======================
        #       BLUR
        # ======================
        scale = 0.25
        blurred = background_area
        for _ in range(4):
            small = smoothscale(
                blurred, (max(1, int(width * scale)), max(1, int(height * scale)))
            )
            blurred = smoothscale(small, (width, height)).convert_alpha()

        # ======================
        #       MÁSCARA
        # ======================
        mask = Surface((width, height), SRCALPHA)
        mask.fill((0, 0, 0, 0))
        rect(mask, (127, 15, 14, 255), (0, 0, width, height), border_radius=radius)

        final_surf = Surface((width, height), SRCALPHA)
        final_surf.blit(blurred, (0, 0))
        final_surf.blit(mask, (0, 0), special_flags=BLEND_RGBA_MULT)

        # overlay escuro
        overlay = Surface((width, height), SRCALPHA)
        rect(overlay, (0, 0, 0, 90), (0, 0, width, height), border_radius=radius)

        # ======================
        #       RENDER FINAL
        # ======================
        self.screen.blit(final_surf, (final_x, panel_y))
        self.screen.blit(overlay, (final_x, panel_y))

        # borda
        rect(
            self.screen,
            (239, 153, 34, 255),
            (final_x, panel_y, width, height),
            width=3,
            border_radius=radius
        )





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
        self.frame_count = 0
        self.chose_on = True

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
        self.update_visual_fade()
