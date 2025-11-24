"""Login Screen - tela de autenticação e registro de usuários"""

import pygame

from view.base_screen import BaseScreen

# Constantes para códigos de erro retornados pelo repositório
USER_EXISTS_ERROR = "Usuário já existe"


class LoginScreen(BaseScreen):
    """Tela de login/registro de usuários"""

    def __init__(self, ranking_controller):
        super().__init__("Login - Batalha Naval")
        self._ranking_controller = ranking_controller

        # Input fields
        self._username_input = ""
        self._password_input = ""
        self._active_field = "username"  # "username" or "password"

        self._create_ui_elements()

        # Feedback message
        self._message = ""
        self._message_color = (255, 255, 255)
        self._message_timer = 0

        # Load click sound
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

    def _create_ui_elements(self):
        """Cria caixas de entrada e botões"""
        # Input boxes
        box_width = 500
        box_height = 60
        box_x = (self._width - box_width) // 2

        self._username_box = pygame.Rect(box_x, 350, box_width, box_height)
        self._password_box = pygame.Rect(box_x, 460, box_width, box_height)

        # Buttons
        button_width = 220
        button_height = 65
        spacing = 30
        total_width = button_width * 2 + spacing
        start_x = (self._width - total_width) // 2

        self._buttons = [
            {
                "text": "Entrar",
                "rect": pygame.Rect(start_x, 600, button_width, button_height),
                "color": (50, 150, 50),
                "hover_color": (100, 200, 100),
                "action": "login",
            },
            {
                "text": "Registrar",
                "rect": pygame.Rect(
                    start_x + button_width + spacing, 600, button_width, button_height
                ),
                "color": (50, 100, 200),
                "hover_color": (100, 150, 255),
                "action": "register",
            },
        ]

        # Return button (centered below)
        self._return_button = {
            "text": "Voltar",
            "rect": pygame.Rect(
                (self._width - button_width) // 2, 690, button_width, button_height
            ),
            "color": (139, 0, 0),
            "hover_color": (200, 0, 0),
        }

    def draw(self):
        # Draw animated background
        self.draw_background()

        # Title with shadow
        title_font = pygame.font.Font(None, 86)
        title_text = "LOGIN"

        # Shadow
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_x = self._width // 2 - shadow.get_width() // 2 + 3
        self._screen.blit(shadow, (shadow_x, 103))

        # Title
        title = title_font.render(title_text, True, (255, 215, 0))
        title_x = self._width // 2 - title.get_width() // 2
        self._screen.blit(title, (title_x, 100))

        # Subtitle
        subtitle_font = pygame.font.Font(None, 34)
        subtitle = subtitle_font.render(
            "Autentique-se para salvar seu progresso", True, (255, 255, 255)
        )
        self._screen.blit(subtitle, (self._width // 2 - subtitle.get_width() // 2, 200))

        # Info box
        info_box_rect = pygame.Rect(self._width // 2 - 300, 250, 600, 60)
        info_surface = pygame.Surface((600, 60), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 180))
        self._screen.blit(info_surface, (info_box_rect.x, info_box_rect.y))
        pygame.draw.rect(self._screen, (139, 0, 0), info_box_rect, 2, border_radius=8)

        info_font = pygame.font.Font(None, 24)
        info_text = info_font.render(
            "Use TAB para alternar campos | ENTER para entrar", True, (255, 255, 255)
        )
        self._screen.blit(
            info_text, (self._width // 2 - info_text.get_width() // 2, 270)
        )

        # Labels
        label_font = pygame.font.Font(None, 30)
        username_label = label_font.render("Usuario:", True, (255, 255, 255))
        password_label = label_font.render("Senha:", True, (255, 255, 255))
        self._screen.blit(
            username_label, (self._username_box.x, self._username_box.y - 35)
        )
        self._screen.blit(
            password_label, (self._password_box.x, self._password_box.y - 35)
        )

        # Input boxes with glow effect for active field
        for box, field_name in [
            (self._username_box, "username"),
            (self._password_box, "password"),
        ]:
            is_active = self._active_field == field_name

            # Glow effect for active field
            if is_active:
                glow_surface = pygame.Surface(
                    (box.width + 10, box.height + 10), pygame.SRCALPHA
                )
                glow_surface.fill((100, 150, 255, 80))
                self._screen.blit(glow_surface, (box.x - 5, box.y - 5))

            # Box background
            box_surface = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 0, 200) if not is_active else (20, 40, 80, 220))
            self._screen.blit(box_surface, (box.x, box.y))

            # Border
            border_color = (100, 150, 255) if is_active else (139, 0, 0)
            pygame.draw.rect(self._screen, border_color, box, 3, border_radius=8)

        # Input text
        input_font = pygame.font.Font(None, 40)
        username_text = input_font.render(
            self._username_input + ("_" if self._active_field == "username" else ""),
            True,
            (255, 255, 255),
        )
        password_display = "*" * len(self._password_input) + (
            "_" if self._active_field == "password" else ""
        )
        password_text = input_font.render(password_display, True, (255, 255, 255))

        self._screen.blit(
            username_text, (self._username_box.x + 15, self._username_box.y + 15)
        )
        self._screen.blit(
            password_text, (self._password_box.x + 15, self._password_box.y + 15)
        )

        # Feedback message
        if self._message and self._message_timer > 0:
            msg_font = pygame.font.Font(None, 32)
            msg_surface = msg_font.render(self._message, True, self._message_color)

            # Message box
            msg_box_width = msg_surface.get_width() + 40
            msg_box = pygame.Rect(
                (self._width - msg_box_width) // 2, 540, msg_box_width, 50
            )
            msg_bg = pygame.Surface((msg_box_width, 50), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 200))
            self._screen.blit(msg_bg, (msg_box.x, msg_box.y))
            pygame.draw.rect(
                self._screen, self._message_color, msg_box, 2, border_radius=8
            )

            self._screen.blit(
                msg_surface, (self._width // 2 - msg_surface.get_width() // 2, 552)
            )
            self._message_timer -= 1

        # Draw buttons with hover effect
        button_font = pygame.font.Font(None, 36)
        mouse_pos = pygame.mouse.get_pos()

        for button in self._buttons:
            if button["rect"].collidepoint(mouse_pos):
                color = button["hover_color"]
                # Shadow on hover
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

            text_surf = button_font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self._screen.blit(text_surf, text_rect)

        # Return button
        button = self._return_button
        if button["rect"].collidepoint(mouse_pos):
            color = button["hover_color"]
            shadow_rect = button["rect"].copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self._screen, (0, 0, 0, 128), shadow_rect, border_radius=8)
        else:
            color = button["color"]

        pygame.draw.rect(self._screen, color, button["rect"], border_radius=8)
        pygame.draw.rect(
            self._screen, (255, 255, 255), button["rect"], 3, border_radius=8
        )

        text_surf = button_font.render(button["text"], True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button["rect"].center)
        self._screen.blit(text_surf, text_rect)

        pygame.display.flip()

    def handle_event(self, event):
        """Trata eventos do pygame"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            return self._handle_keypress(event)
        return None

    def _handle_click(self, pos):
        """Trata cliques do mouse"""
        # Check which input field was clicked
        if self._username_box.collidepoint(pos):
            self._active_field = "username"
            return None
        elif self._password_box.collidepoint(pos):
            self._active_field = "password"
            return None

        # Check action buttons
        for button in self._buttons:
            if button["rect"].collidepoint(pos):
                # Play click sound
                if self._click_sound:
                    self._click_sound.play()

                action = button["action"]
                if action == "login":
                    return self._attempt_login()
                elif action == "register":
                    return self._attempt_register()

        # Check return button
        if self._return_button["rect"].collidepoint(pos):
            # Play click sound
            if self._click_sound:
                self._click_sound.play()
            return "session"

        return None

    def _handle_keypress(self, event):
        """Trata entrada do teclado"""
        if event.key == pygame.K_TAB:
            # Switch active field
            self._active_field = (
                "password" if self._active_field == "username" else "username"
            )
            return None
        elif event.key == pygame.K_RETURN:
            # Try to login on Enter
            return self._attempt_login()
        elif event.key == pygame.K_BACKSPACE:
            # Remove last character
            if self._active_field == "username":
                self._username_input = self._username_input[:-1]
            else:
                self._password_input = self._password_input[:-1]
        elif event.key == pygame.K_ESCAPE:
            return "session"
        elif len(event.unicode) > 0 and event.unicode.isprintable():
            # Add character to active field
            if self._active_field == "username" and len(self._username_input) < 20:
                self._username_input += event.unicode
            elif self._active_field == "password" and len(self._password_input) < 20:
                self._password_input += event.unicode

        return None

    def _attempt_login(self):
        """Tenta autenticar usuário"""
        if not self._username_input or not self._password_input:
            self._show_message("Preencha usuário e senha!", (255, 100, 100))
            return None

        # Check if MongoDB is available
        if not self._ranking_controller.mongo:
            self._show_message(
                "MongoDB não configurado. Use o modo offline.", (255, 200, 100)
            )
            return None

        # Try to authenticate
        success, message = self._ranking_controller.authenticate_user(
            self._username_input, self._password_input
        )

        if success:
            self._show_message("Login bem-sucedido!", (100, 255, 100))
            # Sempre retorna para tela de preparação após login
            return ("login_success", self._username_input)
        else:
            self._show_message("Usuário ou senha incorretos!", (255, 100, 100))
            self._password_input = ""
            return None

    def _attempt_register(self):
        """Tenta criar novo usuário"""
        if not self._username_input or not self._password_input:
            self._show_message("Preencha usuário e senha!", (255, 100, 100))
            return None

        if len(self._username_input) < 3:
            self._show_message(
                "Nome de usuário deve ter pelo menos 3 caracteres!", (255, 100, 100)
            )
            return None

        if len(self._password_input) < 6:
            self._show_message(
                "Senha deve ter pelo menos 6 caracteres!", (255, 100, 100)
            )
            return None

        if len(self._password_input) > 20:
            self._show_message(
                "Senha deve ter no máximo 20 caracteres!", (255, 100, 100)
            )
            return None

        # Check if MongoDB is available
        if not self._ranking_controller.mongo:
            self._show_message(
                "MongoDB não configurado. Use o modo offline.", (255, 200, 100)
            )
            return None

        # Try to create user
        success, message = self._ranking_controller.create_user(
            self._username_input, self._password_input
        )

        if success:
            self._show_message("Usuário criado! Faça login.", (100, 255, 100))
            self._password_input = ""
            return None
        else:
            # Mensagem específica baseada no retorno do repositório
            if message == USER_EXISTS_ERROR:
                self._show_message("Usuário já existe!", (255, 100, 100))
            else:
                self._show_message(f"Erro ao criar usuário: {message}", (255, 100, 100))
            return None

    def _show_message(self, text, color):
        """Exibe uma mensagem temporária"""
        self._message = text
        self._message_color = color
        self._message_timer = 180  # 3 seconds at 60 FPS
