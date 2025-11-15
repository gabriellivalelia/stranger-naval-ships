"""GameOverScreen - tela de fim de jogo com estatísticas e opções"""

import pygame

from view.base_screen import BaseScreen


class GameOverScreen(BaseScreen):
    """Tela exibida ao final de uma partida"""

    def __init__(self, won, stats):
        """
        Args:
            won: True se o jogador venceu, False se perdeu
            stats: Dicionário com estatísticas da partida:
                - turns: número de turnos
                - ships_destroyed: navios destruídos
                - accuracy: precisão (0.0 a 1.0)
                - player_name: nome do jogador
                - score: pontuação (se disponível)
        """
        super().__init__("Fim de Jogo - Batalha Naval")
        self.won = won
        self.stats = stats

        # Buttons
        button_width = 250
        button_height = 60
        center_x = self.width // 2 - button_width // 2

        self.new_game_button = pygame.Rect(center_x, 420, button_width, button_height)
        self.menu_button = pygame.Rect(center_x, 500, button_width, button_height)

    def draw(self):
        # Background color based on result
        if self.won:
            bg_color = (20, 40, 30)  # Dark green tint
        else:
            bg_color = (40, 20, 20)  # Dark red tint

        self.screen.fill(bg_color)

        # Title with result
        title_font = pygame.font.Font(None, 96)
        if self.won:
            title_text = "🎉 VITÓRIA! 🎉"
            title_color = (100, 255, 100)
        else:
            title_text = "💥 DERROTA 💥"
            title_color = (255, 100, 100)

        title = title_font.render(title_text, True, title_color)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        if self.won:
            subtitle_text = "Parabéns! Você destruiu toda a frota inimiga!"
        else:
            subtitle_text = "Que pena! O inimigo destruiu sua frota."

        subtitle = subtitle_font.render(subtitle_text, True, (200, 200, 200))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 150))

        # Statistics box
        self._draw_statistics()

        # New Game button
        pygame.draw.rect(
            self.screen, (50, 150, 50), self.new_game_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (100, 200, 100), self.new_game_button, 3, border_radius=10
        )

        button_font = pygame.font.Font(None, 36)
        new_game_text = button_font.render("🎮 Nova Partida", True, (255, 255, 255))
        self.screen.blit(
            new_game_text,
            (
                self.new_game_button.x
                + self.new_game_button.width // 2
                - new_game_text.get_width() // 2,
                self.new_game_button.y + 15,
            ),
        )

        # Menu button
        pygame.draw.rect(
            self.screen, (100, 100, 120), self.menu_button, border_radius=10
        )
        pygame.draw.rect(
            self.screen, (150, 150, 170), self.menu_button, 3, border_radius=10
        )

        menu_text = button_font.render("🏠 Voltar ao Menu", True, (255, 255, 255))
        self.screen.blit(
            menu_text,
            (
                self.menu_button.x
                + self.menu_button.width // 2
                - menu_text.get_width() // 2,
                self.menu_button.y + 15,
            ),
        )

        pygame.display.flip()

    def _draw_statistics(self):
        """Draw game statistics box"""
        # Stats box background
        box_rect = pygame.Rect(self.width // 2 - 250, 220, 500, 180)
        pygame.draw.rect(self.screen, (40, 50, 70), box_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 150, 255), box_rect, 3, border_radius=15)

        # Stats title
        stats_title_font = pygame.font.Font(None, 32)
        stats_title = stats_title_font.render(
            "📊 Estatísticas da Partida", True, (255, 215, 0)
        )
        self.screen.blit(
            stats_title,
            (
                box_rect.x + box_rect.width // 2 - stats_title.get_width() // 2,
                box_rect.y + 15,
            ),
        )

        # Individual stats
        stats_font = pygame.font.Font(None, 28)
        y_offset = box_rect.y + 60
        line_spacing = 35

        stats_lines = [
            f"⚔️  Turnos: {self.stats.get('turns', 0)}",
            f"🚢  Navios destruídos: {self.stats.get('ships_destroyed', 0)}",
            f"🎯  Precisão: {self.stats.get('accuracy', 0) * 100:.1f}%",
        ]

        # Add score if available
        if "score" in self.stats and self.stats["score"] is not None:
            stats_lines.append(f"⭐  Pontuação: {self.stats['score']}")

        for line in stats_lines:
            text = stats_font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (box_rect.x + 40, y_offset))
            y_offset += line_spacing

    def check_click(self, pos):
        """Handle mouse clicks"""
        if self.new_game_button.collidepoint(pos):
            # Start a new game (go to session screen)
            return "session"
        elif self.menu_button.collidepoint(pos):
            # Return to main menu
            return "home"

        return None
