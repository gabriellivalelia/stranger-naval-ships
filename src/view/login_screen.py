"""Login Screen - tela de autenticação e registro de usuários"""

import pygame

from view.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    """Tela de login/registro de usuários"""

    def __init__(self, ranking_controller, return_to="ranking"):
        super().__init__("Login - Batalha Naval")
        self.ranking_controller = ranking_controller
        self.return_to = return_to  # Where to go after login: "ranking" or "prepare"

        # Input fields
        self.username_input = ""
        self.password_input = ""
        self.active_field = "username"  # "username" or "password"

        # Buttons
        button_width = 200
        button_height = 50
        center_x = self.width // 2 - button_width // 2

        self.login_button = pygame.Rect(
            center_x - 110, 400, button_width, button_height
        )
        self.register_button = pygame.Rect(
            center_x + 110, 400, button_width, button_height
        )
        self.return_button = pygame.Rect(
            center_x + 110, 500, button_width, button_height
        )

        # Input boxes
        self.username_box = pygame.Rect(self.width // 2 - 200, 200, 400, 50)
        self.password_box = pygame.Rect(self.width // 2 - 200, 280, 400, 50)

        # Feedback message
        self.message = ""
        self.message_color = (255, 255, 255)
        self.message_timer = 0

    def draw(self):
        self.screen.fill((20, 30, 50))

        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("🔐 Login", True, (255, 215, 0))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Labels
        label_font = pygame.font.Font(None, 32)
        username_label = label_font.render("Usuário:", True, (255, 255, 255))
        password_label = label_font.render("Senha:", True, (255, 255, 255))
        self.screen.blit(
            username_label, (self.username_box.x, self.username_box.y - 35)
        )
        self.screen.blit(
            password_label, (self.password_box.x, self.password_box.y - 35)
        )

        # Input boxes
        username_color = (
            (100, 150, 255) if self.active_field == "username" else (70, 70, 90)
        )
        password_color = (
            (100, 150, 255) if self.active_field == "password" else (70, 70, 90)
        )

        pygame.draw.rect(
            self.screen, username_color, self.username_box, border_radius=5
        )
        pygame.draw.rect(
            self.screen, password_color, self.password_box, border_radius=5
        )
        pygame.draw.rect(
            self.screen, (200, 200, 200), self.username_box, 2, border_radius=5
        )
        pygame.draw.rect(
            self.screen, (200, 200, 200), self.password_box, 2, border_radius=5
        )

        # Input text
        input_font = pygame.font.Font(None, 36)
        username_text = input_font.render(self.username_input, True, (255, 255, 255))
        password_text = input_font.render(
            "*" * len(self.password_input), True, (255, 255, 255)
        )

        self.screen.blit(
            username_text, (self.username_box.x + 10, self.username_box.y + 12)
        )
        self.screen.blit(
            password_text, (self.password_box.x + 10, self.password_box.y + 12)
        )

        # Buttons
        pygame.draw.rect(
            self.screen, (50, 150, 50), self.login_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (50, 100, 200), self.register_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (200, 50, 50), self.return_button, border_radius=10
        )

        button_font = pygame.font.Font(None, 32)
        login_text = button_font.render("Entrar", True, (255, 255, 255))
        register_text = button_font.render("Registrar", True, (255, 255, 255))
        return_text = button_font.render("Voltar", True, (255, 255, 255))

        self.screen.blit(
            login_text, (self.login_button.x + 60, self.login_button.y + 12)
        )
        self.screen.blit(
            register_text, (self.register_button.x + 45, self.register_button.y + 12)
        )
        self.screen.blit(
            return_text, (self.return_button.x + 60, self.return_button.y + 12)
        )

        # Feedback message
        if self.message and self.message_timer > 0:
            msg_font = pygame.font.Font(None, 28)
            msg_surface = msg_font.render(self.message, True, self.message_color)
            self.screen.blit(
                msg_surface, (self.width // 2 - msg_surface.get_width() // 2, 350)
            )
            self.message_timer -= 1

        # Instructions
        info_font = pygame.font.Font(None, 24)
        info = info_font.render(
            "Clique nos campos para digitar. Use TAB para alternar.",
            True,
            (180, 180, 180),
        )
        self.screen.blit(info, (self.width // 2 - info.get_width() // 2, 560))

        pygame.display.flip()

    def handle_event(self, event):
        """Handles pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            return self._handle_keypress(event)
        return None

    def _handle_click(self, pos):
        """Handle mouse clicks"""
        # Check which input field was clicked
        if self.username_box.collidepoint(pos):
            self.active_field = "username"
            return None
        elif self.password_box.collidepoint(pos):
            self.active_field = "password"
            return None

        # Check buttons
        if self.login_button.collidepoint(pos):
            return self._attempt_login()
        elif self.register_button.collidepoint(pos):
            return self._attempt_register()
        elif self.return_button.collidepoint(pos):
            return self.return_to  # Go back to where we came from

        return None

    def _handle_keypress(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_TAB:
            # Switch active field
            self.active_field = (
                "password" if self.active_field == "username" else "username"
            )
            return None
        elif event.key == pygame.K_RETURN:
            # Try to login on Enter
            return self._attempt_login()
        elif event.key == pygame.K_BACKSPACE:
            # Remove last character
            if self.active_field == "username":
                self.username_input = self.username_input[:-1]
            else:
                self.password_input = self.password_input[:-1]
        elif event.key == pygame.K_ESCAPE:
            return "ranking"
        elif len(event.unicode) > 0 and event.unicode.isprintable():
            # Add character to active field
            if self.active_field == "username" and len(self.username_input) < 20:
                self.username_input += event.unicode
            elif self.active_field == "password" and len(self.password_input) < 30:
                self.password_input += event.unicode

        return None

    def _attempt_login(self):
        """Try to authenticate user"""
        if not self.username_input or not self.password_input:
            self._show_message("Preencha usuário e senha!", (255, 100, 100))
            return None

        # Check if MongoDB is available
        if not self.ranking_controller.mongo:
            self._show_message(
                "MongoDB não configurado. Use o modo offline.", (255, 200, 100)
            )
            return None

        # Try to authenticate
        success = self.ranking_controller.mongo.authenticate_user(
            self.username_input, self.password_input
        )

        if success:
            self._show_message("Login bem-sucedido! ✓", (100, 255, 100))
            # Return with username - will go to ranking or prepare depending on return_to
            if self.return_to == "prepare":
                return ("login_success", self.username_input)
            else:
                return ("ranking", self.username_input)
        else:
            self._show_message("Usuário ou senha incorretos!", (255, 100, 100))
            self.password_input = ""
            return None

    def _attempt_register(self):
        """Try to create new user"""
        if not self.username_input or not self.password_input:
            self._show_message("Preencha usuário e senha!", (255, 100, 100))
            return None

        if len(self.password_input) < 4:
            self._show_message(
                "Senha deve ter pelo menos 4 caracteres!", (255, 100, 100)
            )
            return None

        # Check if MongoDB is available
        if not self.ranking_controller.mongo:
            self._show_message(
                "MongoDB não configurado. Use o modo offline.", (255, 200, 100)
            )
            return None

        # Try to create user
        success = self.ranking_controller.mongo.create_user(
            self.username_input, self.password_input
        )

        if success:
            self._show_message("Usuário criado! Faça login.", (100, 255, 100))
            self.password_input = ""
            return None
        else:
            self._show_message("Usuário já existe ou erro ao criar!", (255, 100, 100))
            return None

    def _show_message(self, text, color):
        """Display a temporary message"""
        self.message = text
        self.message_color = color
        self.message_timer = 180  # 3 seconds at 60 FPS
