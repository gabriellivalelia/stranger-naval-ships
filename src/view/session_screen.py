"""SessionScreen - tela para escolher entre jogar como guest ou fazer login"""

import pygame

from view.base_screen import BaseScreen


class SessionScreen(BaseScreen):
    """Tela de escolha de sessão antes de iniciar o jogo"""

    def __init__(self):
        super().__init__("Sessão - Batalha Naval")

        # Buttons
        button_width = 300
        button_height = 60
        center_x = self.width // 2 - button_width // 2

        self.guest_button = pygame.Rect(center_x, 280, button_width, button_height)
        self.login_button = pygame.Rect(center_x, 370, button_width, button_height)
        self.back_button = pygame.Rect(center_x, 460, button_width, button_height)

    def draw(self):
        self.screen.fill((20, 30, 50))

        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("⚓ Bem-vindo!", True, (255, 215, 0))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))

        # Subtitle
        subtitle_font = pygame.font.Font(None, 32)
        subtitle = subtitle_font.render(
            "Como você deseja jogar?", True, (200, 200, 200)
        )
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 150))

        # Info message
        info_font = pygame.font.Font(None, 26)
        info_lines = [
            "Crie uma conta para salvar seu progresso",
            "e competir no ranking mundial!",
        ]

        y_offset = 200
        for line in info_lines:
            info_text = info_font.render(line, True, (150, 200, 255))
            self.screen.blit(
                info_text, (self.width // 2 - info_text.get_width() // 2, y_offset)
            )
            y_offset += 30

        # Guest button
        pygame.draw.rect(
            self.screen, (100, 100, 120), self.guest_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (150, 150, 170), self.guest_button, 3, border_radius=10
        )

        button_font = pygame.font.Font(None, 36)
        guest_text = button_font.render("🎮 Entrar como Guest", True, (255, 255, 255))
        self.screen.blit(
            guest_text,
            (
                self.guest_button.x
                + self.guest_button.width // 2
                - guest_text.get_width() // 2,
                self.guest_button.y + 15,
            ),
        )

        # Login button
        pygame.draw.rect(
            self.screen, (50, 150, 50), self.login_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (100, 200, 100), self.login_button, 3, border_radius=10
        )

        login_text = button_font.render("🔐 Iniciar Sessão", True, (255, 255, 255))
        self.screen.blit(
            login_text,
            (
                self.login_button.x
                + self.login_button.width // 2
                - login_text.get_width() // 2,
                self.login_button.y + 15,
            ),
        )

        # Back button
        pygame.draw.rect(self.screen, (200, 50, 50), self.back_button, border_radius=10)

        back_text = button_font.render("← Voltar", True, (255, 255, 255))
        self.screen.blit(
            back_text,
            (
                self.back_button.x
                + self.back_button.width // 2
                - back_text.get_width() // 2,
                self.back_button.y + 15,
            ),
        )

        # Footer hint
        hint_font = pygame.font.Font(None, 22)
        hint = hint_font.render(
            "💡 Modo Guest: sem ranking, apenas diversão!", True, (180, 180, 180)
        )
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, 540))

        pygame.display.flip()

    def check_click(self, pos):
        """Handle mouse clicks"""
        if self.guest_button.collidepoint(pos):
            # Play as guest (no user tracking)
            return ("prepare", None)
        elif self.login_button.collidepoint(pos):
            # Go to login screen
            return "login"
        elif self.back_button.collidepoint(pos):
            # Return to home
            return "home"

        return None
