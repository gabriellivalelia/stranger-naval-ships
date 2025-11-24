"""SessionScreen - tela para escolher entre jogar como guest ou fazer login"""

import pygame

from view.base_screen import BaseScreen


class SessionScreen(BaseScreen):
    """Tela de escolha de sessão antes de iniciar o jogo"""

    def __init__(self, previous_user=None):
        super().__init__("Sessão - Batalha Naval")

        self._previous_user = previous_user  # Usuário logado anteriormente

        self._create_buttons()

        # Carrega som de clique
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

    def _create_buttons(self):
        """Cria botões estilizados"""
        button_width = 300
        button_height = 70
        center_x = self._width // 2 - button_width // 2

        self._buttons = []

        # Se há usuário anterior, adiciona botão "Continuar como..."
        if self._previous_user:
            # Trunca nome se muito longo para caber no botão
            # Limita a 15 caracteres para garantir que caiba com "Continuar como "
            max_name_length = 15
            if len(self._previous_user) > max_name_length:
                display_name = self._previous_user[:max_name_length] + "..."
            else:
                display_name = self._previous_user

            button_text = f"Continuar como {display_name}"

            # Calcula tamanho de fonte apropriado baseado no comprimento do texto
            # Quanto mais longo o texto, menor a fonte
            if len(button_text) > 25:
                font_size = 28
            elif len(button_text) > 22:
                font_size = 30
            else:
                font_size = 32

            self._buttons.append(
                {
                    "text": button_text,
                    "rect": pygame.Rect(center_x, 420, button_width, button_height),
                    "color": (50, 100, 200),
                    "hover_color": (100, 150, 255),
                    "action": "continue",
                    "font_size": font_size,
                }
            )
            # Ajusta posição dos outros botões
            guest_y = 510
            login_y = 600
            back_y = 690
        else:
            # Posições originais
            guest_y = 450
            login_y = 540
            back_y = 630

        self._buttons.extend(
            [
                {
                    "text": "Entrar como Guest",
                    "rect": pygame.Rect(center_x, guest_y, button_width, button_height),
                    "color": (100, 100, 120),
                    "hover_color": (150, 150, 170),
                    "action": "guest",
                },
                {
                    "text": "Iniciar Sessao",
                    "rect": pygame.Rect(center_x, login_y, button_width, button_height),
                    "color": (50, 150, 50),
                    "hover_color": (100, 200, 100),
                    "action": "login",
                },
                {
                    "text": "Voltar",
                    "rect": pygame.Rect(center_x, back_y, button_width, button_height),
                    "color": (139, 0, 0),
                    "hover_color": (200, 0, 0),
                    "action": "back",
                },
            ]
        )

    def draw(self):
        # Desenha fundo animado
        self.draw_background()

        # Título com sombra
        title_font = pygame.font.Font(None, 80)
        title_text = "BEM-VINDO!"

        # Sombra
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_x = self._width // 2 - shadow.get_width() // 2 + 3
        self._screen.blit(shadow, (shadow_x, 103))

        # Título
        title = title_font.render(title_text, True, (255, 215, 0))
        title_x = self._width // 2 - title.get_width() // 2
        self._screen.blit(title, (title_x, 100))

        # Subtítulo
        subtitle_font = pygame.font.Font(None, 40)
        subtitle = subtitle_font.render(
            "Como você deseja jogar?", True, (255, 255, 255)
        )
        self._screen.blit(subtitle, (self._width // 2 - subtitle.get_width() // 2, 200))

        # Caixa de informações
        info_box_rect = pygame.Rect(self._width // 2 - 350, 270, 700, 120)
        info_surface = pygame.Surface((700, 120), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 180))
        self._screen.blit(info_surface, (info_box_rect.x, info_box_rect.y))
        pygame.draw.rect(self._screen, (139, 0, 0), info_box_rect, 3, border_radius=10)

        # Texto de informações
        info_font = pygame.font.Font(None, 28)
        info_lines = [
            "Crie uma conta para salvar seu progresso",
            "e competir no ranking mundial!",
            "Modo Guest: sem ranking, apenas diversao!",
        ]

        y_offset = 285
        for line in info_lines:
            info_text = info_font.render(line, True, (255, 255, 255))
            self._screen.blit(
                info_text, (self._width // 2 - info_text.get_width() // 2, y_offset)
            )
            y_offset += 35

        # Desenha botões com efeito hover
        mouse_pos = pygame.mouse.get_pos()

        for button in self._buttons:
            if button["rect"].collidepoint(mouse_pos):
                color = button["hover_color"]
                # Sombra ao passar mouse
                shadow_rect = button["rect"].copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(
                    self._screen, (0, 0, 0, 128), shadow_rect, border_radius=8
                )
            else:
                color = button["color"]

            pygame.draw.rect(self._screen, color, button["rect"], border_radius=8)
            pygame.draw.rect(
                self._screen, (255, 255, 255), button["rect"], 3, border_radius=8
            )

            # Usa fonte personalizada se o botão especificar, senão usa padrão
            font_size = button.get("font_size", 38)
            button_font = pygame.font.Font(None, font_size)

            text_surf = button_font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self._screen.blit(text_surf, text_rect)

        pygame.display.flip()

    def check_click(self, pos):
        """Trata cliques do mouse"""
        for button in self._buttons:
            if button["rect"].collidepoint(pos):
                # Toca som de clique
                if self._click_sound:
                    self._click_sound.play()

                action = button["action"]
                if action == "continue":
                    # Continua com usuário anterior
                    return ("login_success", self._previous_user)
                elif action == "guest":
                    return ("prepare", None)
                elif action == "login":
                    return "login"
                elif action == "back":
                    return "home"
        return None
