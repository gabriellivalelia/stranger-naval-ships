import pygame

from view.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    def __init__(self):
        super().__init__("Menu - Stranger Things Naval Battle")
        self._font = pygame.font.Font(None, 48)
        self._buttons = self._create_buttons()

        # Carrega logo
        self._logo = None
        try:
            logo_img = pygame.image.load("src/assets/logo/logo.png")
            # Redimensiona logo mantendo proporção
            logo_width = 500
            logo_ratio = logo_img.get_height() / logo_img.get_width()
            logo_height = int(logo_width * logo_ratio)
            self._logo = pygame.transform.scale(logo_img, (logo_width, logo_height))
            self._logo = self._logo.convert_alpha()
        except Exception as e:
            print(f"Não foi possível carregar logo: {e}")
            self._logo = None

        # Carrega e toca música de fundo
        try:
            pygame.mixer.music.load("src/assets/sounds/tema.mp3")
            pygame.mixer.music.set_volume(0.3)  # Volume em 30%
            pygame.mixer.music.play(-1)  # Loop infinito
        except Exception as e:
            print(f"Não foi possível carregar música de fundo: {e}")

        # Carrega som de clique
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

    def _create_buttons(self):
        # Centraliza botões horizontalmente
        button_width = 250
        button_height = 60
        button_x = (self._width - button_width) // 2

        return [
            {
                "text": "Jogar",
                "rect": pygame.Rect(button_x, 550, button_width, button_height),
                "color": (139, 0, 0),
                "hover_color": (200, 0, 0),
                "action": "session",
            },
            {
                "text": "Ranking",
                "rect": pygame.Rect(button_x, 630, button_width, button_height),
                "color": (139, 0, 0),
                "hover_color": (200, 0, 0),
                "action": "ranking",
            },
            {
                "text": "Sair",
                "rect": pygame.Rect(button_x, 710, button_width, button_height),
                "color": (139, 0, 0),
                "hover_color": (200, 0, 0),
                "action": "exit",
            },
        ]

    def draw(self):
        # Desenha fundo
        self.draw_background()

        # Desenha logo (centralizado horizontalmente, posicionado no topo)
        if self._logo:
            logo_x = (self._width - self._logo.get_width()) // 2
            logo_y = 80
            self._screen.blit(self._logo, (logo_x, logo_y))
        else:
            # Fallback para texto se logo não carregar
            title_text = self._font.render(
                "BATALHA NAVAL - STRANGER THINGS", True, (255, 0, 0)
            )
            title_x = (self._width - title_text.get_width()) // 2
            self._screen.blit(title_text, (title_x, 100))

        # Botões com estilo aprimorado
        button_font = pygame.font.Font(None, 42)
        mouse_pos = pygame.mouse.get_pos()

        for button in self._buttons:
            # Determina cor do botão
            if button["rect"].collidepoint(mouse_pos):
                color = button["hover_color"]
                # Adiciona efeito de sombra ao passar mouse
                shadow_rect = button["rect"].copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(
                    self._screen, (0, 0, 0, 128), shadow_rect, border_radius=8
                )
            else:
                color = button["color"]

            # Desenha botão com cantos arredondados
            pygame.draw.rect(self._screen, color, button["rect"], border_radius=8)
            pygame.draw.rect(
                self._screen, (255, 255, 255), button["rect"], 3, border_radius=8
            )

            # Desenha texto do botão
            text_surf = button_font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self._screen.blit(text_surf, text_rect)

        pygame.display.flip()

    def check_click(self, pos):
        for button in self._buttons:
            if button["rect"].collidepoint(pos):
                # Toca som de clique
                if self._click_sound:
                    self._click_sound.play()
                return button["action"]
        return None
