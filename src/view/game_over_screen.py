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
                - ships_remaining: navios próprios sobreviventes
                - accuracy: precisão (0.0 a 1.0)
                - player_name: nome do jogador
                - score: pontuação (se disponível)
        """
        super().__init__("Fim de Jogo - Batalha Naval")
        self._won = won
        self._stats = stats

        self._create_buttons()

        # Load click sound
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

        # Load and play win/lost music based on result
        try:
            if won:
                pygame.mixer.music.load("src/assets/sounds/win.mp3")
            else:
                pygame.mixer.music.load("src/assets/sounds/lost.mp3")
            pygame.mixer.music.set_volume(0.4)  # Volume at 40%
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except Exception as e:
            print(f"Não foi possível carregar música de fim de jogo: {e}")

    def _create_buttons(self):
        """Cria botões estilizados"""
        button_width = 280
        button_height = 70
        center_x = self._width // 2 - button_width // 2

        self._buttons = [
            {
                "text": "Nova Partida",
                "rect": pygame.Rect(center_x, 630, button_width, button_height),
                "color": (50, 150, 50),
                "hover_color": (100, 200, 100),
                "action": "new_game",
            },
            {
                "text": "Voltar ao Menu",
                "rect": pygame.Rect(center_x, 720, button_width, button_height),
                "color": (139, 0, 0),
                "hover_color": (200, 0, 0),
                "action": "menu",
            },
        ]

    def draw(self):
        # Draw animated background
        self.draw_background()

        # Title with result and shadow
        title_font = pygame.font.Font(None, 100)
        if self._won:
            title_text = "VITORIA!"
            title_color = (100, 255, 100)
        else:
            title_text = "DERROTA"
            title_color = (255, 100, 100)

        # Shadow
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_x = self._width // 2 - shadow.get_width() // 2 + 3
        self._screen.blit(shadow, (shadow_x, 83))

        # Title
        title = title_font.render(title_text, True, title_color)
        title_x = self._width // 2 - title.get_width() // 2
        self._screen.blit(title, (title_x, 80))

        # Subtitle
        subtitle_font = pygame.font.Font(None, 38)
        if self._won:
            subtitle_text = "Parabéns! Você destruiu toda a frota inimiga!"
        else:
            subtitle_text = "Que pena! O inimigo destruiu sua frota."

        subtitle = subtitle_font.render(subtitle_text, True, (255, 255, 255))
        self._screen.blit(subtitle, (self._width // 2 - subtitle.get_width() // 2, 200))

        # Statistics box
        self._draw_statistics()

        # Draw buttons with hover effect
        button_font = pygame.font.Font(None, 40)
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

        pygame.display.flip()

    def _draw_statistics(self):
        """Desenha caixa de estatísticas do jogo com estilo aprimorado"""
        # Stats box background
        box_width = 700
        box_height = 340
        box_x = (self._width - box_width) // 2
        box_y = 270
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        # Semi-transparent background
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, 200))
        self._screen.blit(box_surface, (box_x, box_y))

        # Border with result color
        border_color = (100, 255, 100) if self._won else (255, 100, 100)
        pygame.draw.rect(self._screen, border_color, box_rect, 4, border_radius=12)

        # Stats title
        stats_title_font = pygame.font.Font(None, 42)
        stats_title = stats_title_font.render(
            "ESTATISTICAS DA PARTIDA", True, (255, 215, 0)
        )
        self._screen.blit(
            stats_title,
            (box_x + box_width // 2 - stats_title.get_width() // 2, box_y + 20),
        )

        # Separator line
        pygame.draw.line(
            self._screen,
            border_color,
            (box_x + 40, box_y + 70),
            (box_x + box_width - 40, box_y + 70),
            2,
        )

        # Individual stats with icons
        stats_font = pygame.font.Font(None, 36)
        y_offset = box_y + 100
        line_spacing = 55

        stats_lines = [
            f"Turnos: {self._stats.get('turns', 0)}",
            f"Navios Sobreviventes: {self._stats.get('ships_remaining', 0)}",
            f"Precisão: {self._stats.get('accuracy', 0) * 100:.1f}%",
        ]

        # Add score if available
        if "score" in self._stats and self._stats["score"] is not None:
            stats_lines.append(f"Pontuação: {self._stats['score']}")

        for line in stats_lines:
            text = stats_font.render(line, True, (255, 255, 255))
            self._screen.blit(text, (box_x + 60, y_offset))
            y_offset += line_spacing

    def check_click(self, pos):
        """Trata cliques do mouse"""
        for button in self._buttons:
            if button["rect"].collidepoint(pos):
                # Play click sound
                if self._click_sound:
                    self._click_sound.play()

                action = button["action"]
                if action == "new_game":
                    return "session"
                elif action == "menu":
                    return "home"
        return None
