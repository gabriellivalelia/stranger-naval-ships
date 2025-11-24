import pygame

from view.base_screen import BaseScreen


class RankingScreen(BaseScreen):
    def __init__(self, ranking_controller, current_user=None):
        super().__init__("Ranking - Batalha Naval")
        self._ranking_controller = ranking_controller
        self._current_user = current_user  # Usuário logado (se houver)

        # Carrega rankings
        self._rankings = []
        self._user_stats = None
        self._load_data()

        # Cria botão
        self._create_button()

        # Carrega som de clique
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

    def _create_button(self):
        """Cria botão de retorno centralizado"""
        button_width = 250
        button_height = 60
        button_x = (self._width - button_width) // 2
        button_y = 800

        self._return_button = {
            "text": "Voltar",
            "rect": pygame.Rect(button_x, button_y, button_width, button_height),
            "color": (139, 0, 0),
            "hover_color": (200, 0, 0),
        }

    def _load_data(self):
        """Carrega dados de ranking do controller"""
        try:
            self._rankings = self._ranking_controller.get_top_rankings(10)
            if self._current_user:
                self._user_stats = self._ranking_controller.get_player_stats(
                    self._current_user
                )
        except Exception as e:
            print(f"Erro ao carregar rankings: {e}")
            self._rankings = []

    def draw(self):
        # Desenha fundo animado
        self.draw_background()

        # Título com efeito de sombra
        title_font = pygame.font.Font(None, 72)
        title_text = "TOP 10 RANKINGS"

        # Desenha sombra do título
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_x = self._width // 2 - shadow.get_width() // 2 + 3
        shadow_y = 53
        self._screen.blit(shadow, (shadow_x, shadow_y))

        # Desenha título
        title = title_font.render(title_text, True, (255, 215, 0))
        title_x = self._width // 2 - title.get_width() // 2
        title_y = 50
        self._screen.blit(title, (title_x, title_y))

        # Exibe rankings
        if self._rankings:
            self._draw_rankings()
        else:
            msg_font = pygame.font.Font(None, 40)
            msg = msg_font.render(
                "Nenhum ranking disponível ainda", True, (255, 255, 255)
            )
            self._screen.blit(msg, (self._width // 2 - msg.get_width() // 2, 400))

        # Exibe estatísticas do usuário se disponível
        if self._user_stats:
            self._draw_user_stats()

        # Desenha botão de retorno com estilo
        button = self._return_button
        mouse_pos = pygame.mouse.get_pos()

        if button["rect"].collidepoint(mouse_pos):
            color = button["hover_color"]
            # Sombra ao passar mouse
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

        button_font = pygame.font.Font(None, 42)
        button_text = button_font.render(button["text"], True, (255, 255, 255))
        text_rect = button_text.get_rect(center=button["rect"].center)
        self._screen.blit(button_text, text_rect)

        pygame.display.flip()

    def _draw_rankings(self):
        """Desenha a lista de ranking com estilo aprimorado"""
        start_y = 160
        row_height = 50

        # Desenha caixa semi-transparente para rankings
        box_rect = pygame.Rect(80, start_y - 20, self._width - 160, 580)
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, 180))
        self._screen.blit(box_surface, (box_rect.x, box_rect.y))
        pygame.draw.rect(self._screen, (139, 0, 0), box_rect, 3, border_radius=10)

        # Cabeçalho
        header_font = pygame.font.Font(None, 32)
        header_y = start_y + 5

        # Cabeçalhos das colunas com melhor espaçamento
        col_x = [150, 400, 750, 1050]
        headers = ["#", "Jogador", "Pontos", "Precisão"]

        for i, header_text in enumerate(headers):
            header = header_font.render(header_text, True, (255, 215, 0))
            self._screen.blit(header, (col_x[i], header_y))

        # Desenha linha separadora
        pygame.draw.line(
            self._screen,
            (139, 0, 0),
            (100, start_y + 40),
            (self._width - 100, start_y + 40),
            2,
        )

        # Rankings
        for i, rank in enumerate(self._rankings[:10]):
            y = start_y + 60 + (i * row_height)

            # Destaca usuário atual
            is_current_user = rank.get("player_name") == self._current_user

            # Fundo alternado das linhas
            if i % 2 == 0:
                row_surface = pygame.Surface(
                    (box_rect.width - 40, row_height - 10), pygame.SRCALPHA
                )
                row_surface.fill((255, 255, 255, 15))
                self._screen.blit(row_surface, (box_rect.x + 20, y - 5))

            color = (255, 215, 0) if is_current_user else (255, 255, 255)
            font = pygame.font.Font(None, 30)

            # Desenha número da posição
            rank_text = f"{i + 1}"
            text = font.render(rank_text, True, color)
            self._screen.blit(text, (col_x[0], y))

            # Nome do jogador (trunca se muito longo)
            player_name = rank.get("player_name", "Unknown")[:20]
            text = font.render(player_name, True, color)
            self._screen.blit(text, (col_x[1], y))

            # Pontuação
            score = rank.get("score", 0)
            text = font.render(str(score), True, color)
            self._screen.blit(text, (col_x[2], y))

            # Precisão
            accuracy = rank.get("accuracy", 0)
            text = font.render(f"{accuracy:.1f}%", True, color)
            self._screen.blit(text, (col_x[3], y))

    def _draw_user_stats(self):
        """Desenha caixa de estatísticas do usuário com estilo aprimorado"""
        # Caixa de estatísticas posicionada acima do botão
        box_width = 900
        box_height = 80
        box_x = (self._width - box_width) // 2
        box_y = 700

        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        # Fundo semi-transparente
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, 200))
        self._screen.blit(box_surface, (box_x, box_y))

        # Borda
        pygame.draw.rect(self._screen, (255, 215, 0), box_rect, 3, border_radius=10)

        # Título (trunca nome se muito longo)
        title_font = pygame.font.Font(None, 28)
        display_username = (
            self._current_user[:25] + "..."
            if len(self._current_user) > 25
            else self._current_user
        )
        title = title_font.render(
            f"Estatisticas de {display_username}", True, (255, 215, 0)
        )
        self._screen.blit(title, (box_x + 20, box_y + 10))

        # Estatísticas
        stats_font = pygame.font.Font(None, 26)
        stats = self._user_stats

        stats_text = f"Partidas: {stats['total_matches']}  |  Vitórias: {stats['wins']}  |  Derrotas: {stats['losses']}  |  Taxa: {stats['win_rate']}%  |  Melhor Score: {stats['best_score']}"

        text = stats_font.render(stats_text, True, (255, 255, 255))
        self._screen.blit(text, (box_x + 20, box_y + 45))

    def check_click(self, pos):
        if self._return_button["rect"].collidepoint(pos):
            # Toca som de clique
            if self._click_sound:
                self._click_sound.play()
            return "home"
        return None

    def handle_event(self, event):
        """Trata eventos do mouse do controller. Retorna um nome de tela se navegação for solicitada."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.check_click(event.pos)
        return None
