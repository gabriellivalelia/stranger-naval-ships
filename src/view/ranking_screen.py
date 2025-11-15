import pygame

from view.base_screen import BaseScreen


class RankingScreen(BaseScreen):
    def __init__(self, ranking_controller, current_user=None):
        super().__init__("Ranking - Batalha Naval")
        self.ranking_controller = ranking_controller
        self.current_user = current_user  # Logged in user (if any)

        # Buttons
        self.return_button = pygame.Rect(50, 550, 150, 50)
        self.login_button = pygame.Rect(self.width - 200, 550, 150, 50)

        # Load rankings
        self.rankings = []
        self.user_stats = None
        self._load_data()

    def _load_data(self):
        """Load ranking data from controller"""
        try:
            self.rankings = self.ranking_controller.get_top_rankings(10)
            if self.current_user:
                self.user_stats = self.ranking_controller.get_player_stats(
                    self.current_user
                )
        except Exception as e:
            print(f"Error loading rankings: {e}")
            self.rankings = []

    def draw(self):
        self.screen.fill((20, 30, 50))

        # Title
        title_font = pygame.font.Font(None, 64)
        text = title_font.render("🏆 Top 10 Rankings", True, (255, 215, 0))
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, 30))

        # Display current user if logged in
        if self.current_user:
            user_font = pygame.font.Font(None, 28)
            user_text = user_font.render(
                f"Logado como: {self.current_user}", True, (100, 255, 100)
            )
            self.screen.blit(
                user_text, (self.width // 2 - user_text.get_width() // 2, 85)
            )

        # Display rankings
        if self.rankings:
            self._draw_rankings()
        else:
            msg_font = pygame.font.Font(None, 32)
            msg = msg_font.render(
                "Nenhum ranking disponível ainda", True, (180, 180, 180)
            )
            self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, 300))

        # Display user stats if available
        if self.user_stats:
            self._draw_user_stats()

        # Return button
        pygame.draw.rect(
            self.screen, (200, 50, 50), self.return_button, border_radius=10
        )
        button_font = pygame.font.Font(None, 32)
        button_text = button_font.render("Voltar", True, (255, 255, 255))
        self.screen.blit(
            button_text, (self.return_button.x + 35, self.return_button.y + 12)
        )

        # Login button
        login_color = (50, 100, 200) if not self.current_user else (70, 70, 90)
        pygame.draw.rect(self.screen, login_color, self.login_button, border_radius=10)
        login_text = button_font.render(
            "Login" if not self.current_user else "Logoff", True, (255, 255, 255)
        )
        self.screen.blit(
            login_text, (self.login_button.x + 35, self.login_button.y + 12)
        )

        pygame.display.flip()

    def _draw_rankings(self):
        """Draw the ranking list"""
        start_y = 130
        row_height = 35
        font = pygame.font.Font(None, 26)

        # Header
        header_font = pygame.font.Font(None, 28)
        header = header_font.render(
            f"{'#':<4}{'Jogador':<20}{'Pontos':<12}{'Vitórias':<12}{'Precisão'}",
            True,
            (200, 200, 200),
        )
        self.screen.blit(header, (100, start_y))

        # Rankings
        for i, rank in enumerate(self.rankings[:10]):
            y = start_y + 40 + (i * row_height)

            # Highlight current user
            color = (
                (100, 255, 100)
                if rank.get("player_name") == self.current_user
                else (255, 255, 255)
            )

            # Medal for top 3
            medal = ""
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"

            player_name = rank.get("player_name", "Unknown")[:18]
            score = rank.get("score", 0)
            won = "✓" if rank.get("won") else "✗"
            accuracy = rank.get("accuracy", 0)

            text = font.render(
                f"{medal} {i + 1:<3}{player_name:<20}{score:<12}{won:<12}{accuracy:.1f}%",
                True,
                color,
            )
            self.screen.blit(text, (100, y))

    def _draw_user_stats(self):
        """Draw user statistics box"""
        # Stats box
        box_rect = pygame.Rect(self.width // 2 - 200, 480, 400, 60)
        pygame.draw.rect(self.screen, (40, 50, 70), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 150, 255), box_rect, 2, border_radius=10)

        stats_font = pygame.font.Font(None, 24)
        stats = self.user_stats

        line1 = f"Partidas: {stats['total_matches']}  |  Vitórias: {stats['wins']}  |  Derrotas: {stats['losses']}"
        line2 = f"Taxa de Vitória: {stats['win_rate']}%  |  Melhor Score: {stats['best_score']}"

        text1 = stats_font.render(line1, True, (255, 255, 255))
        text2 = stats_font.render(line2, True, (255, 255, 255))

        self.screen.blit(text1, (box_rect.x + 20, box_rect.y + 10))
        self.screen.blit(text2, (box_rect.x + 20, box_rect.y + 35))

    def check_click(self, pos):
        if self.return_button.collidepoint(pos):
            return "home"
        if self.login_button.collidepoint(pos):
            if self.current_user:
                # Logoff
                return ("ranking_refresh", None)
            else:
                # Go to login
                return "login"
        return None
