import pygame

from controller.play_controller import PlayController
from view.base_screen import BaseScreen


class PlayScreen(BaseScreen):
    def __init__(self, player=None, ranking_controller=None, current_user=None):
        super().__init__("Stranger Ships")

        # Cores
        self.WATER_COLOR = (0, 119, 190)
        self.SHIP_COLOR = (100, 100, 100)
        self.HIT_COLOR = (220, 20, 60)
        self.MISS_COLOR = (255, 255, 255)
        self.GRID_COLOR = (50, 50, 80)
        self.TEXT_COLOR = (255, 255, 255)

        # Configuração da grade
        self._cell_size = 50
        self._player_offset_x = 50
        self._offset_y = 150
        self._enemy_offset_x = 750

        # Inicializa controlador do jogo
        self._controller = PlayController(player=player)
        self._player = self._controller.player
        self._computer = self._controller.computer

        # Sistema de ranking
        self._ranking_controller = ranking_controller
        self._current_user = current_user
        self._ranking_saved = False  # Flag para salvar ranking apenas uma vez

        # Estado do jogo
        self._message = "Seu turno! Clique no tabuleiro inimigo para atacar"
        self._waiting_computer = False
        self._waiting_computer_time = 0

        # Estado da animação de bomba
        self._bomb_animation = (
            None  # {"row": int, "col": int, "board": str, "stage": str, "time": int}
        )
        self._bomb_animation_duration = 600  # ms para animação de bomba
        self._result_animation_duration = 800  # ms para animação de acerto/erro
        self._pending_attack = None  # Armazena dados do ataque durante animação
        self._game_over_pending = False  # Flag para navegar para tela de game over

        # Carrega imagens de bomba
        self._load_bomb_images()

        # Animação de brilho para tabuleiro ativo
        self._glow_alpha = 0
        self._glow_direction = 5
        self._glow_last_update = pygame.time.get_ticks()
        self._glow_update_interval = 30

        # Botão de retorno
        self._return_button = {
            "rect": pygame.Rect(self._width - 170, 20, 150, 50),
            "text": "Voltar",
            "color": (139, 0, 0),
            "hover_color": (200, 0, 0),
        }

        # Carrega som de clique
        self._click_sound = None
        try:
            self._click_sound = pygame.mixer.Sound("src/assets/sounds/click.mp3")
            self._click_sound.set_volume(0.5)
        except Exception as e:
            print(f"Não foi possível carregar som de clique: {e}")

        # Carrega e toca música de guerra
        try:
            pygame.mixer.music.load("src/assets/sounds/war.mp3")
            pygame.mixer.music.set_volume(0.3)  # Volume em 30%
            pygame.mixer.music.play(-1)  # Loop infinito
        except Exception as e:
            print(f"Não foi possível carregar música de guerra: {e}")

        # Carrega sons de acerto e erro
        self._hit_sound = None
        self._miss_sound = None
        try:
            self._hit_sound = pygame.mixer.Sound("src/assets/sounds/hit.mp3")
            self._hit_sound.set_volume(0.6)
        except Exception as e:
            print(f"Não foi possível carregar som de acerto: {e}")

        try:
            self._miss_sound = pygame.mixer.Sound("src/assets/sounds/miss.mp3")
            self._miss_sound.set_volume(0.6)
        except Exception as e:
            print(f"Não foi possível carregar som de erro: {e}")

    def _load_bomb_images(self):
        """Carrega imagens de animação de bomba"""
        self._bomb_images = {}
        try:
            # Tenta diferentes extensões
            for name in ["bomb", "hit", "miss"]:
                loaded = False
                for ext in [".jpg", ".png", ".jpeg"]:
                    try:
                        img = pygame.image.load(f"src/assets/bombs/{name}{ext}")
                        self._bomb_images[name] = img
                        loaded = True
                        break
                    except Exception:
                        continue
                if not loaded:
                    # Cria placeholder
                    surf = pygame.Surface((self._cell_size, self._cell_size))
                    if name == "bomb":
                        surf.fill((255, 165, 0))  # Laranja
                    elif name == "hit":
                        surf.fill((220, 20, 60))  # Vermelho
                    else:
                        surf.fill((255, 255, 255))  # Branco
                    self._bomb_images[name] = surf
        except Exception as e:
            print(f"Erro ao carregar imagens de bomba: {e}")

    def draw(self):
        # Desenha fundo animado
        self.draw_background()

        # Título com sombra
        title_font = pygame.font.Font(None, 70)
        title_text = "STRANGER SHIPS"

        # Sombra
        shadow = title_font.render(title_text, True, (0, 0, 0))
        shadow_x = self._width // 2 - shadow.get_width() // 2 + 3
        self._screen.blit(shadow, (shadow_x, 23))

        # Título
        title = title_font.render(title_text, True, (255, 215, 0))
        title_x = self._width // 2 - title.get_width() // 2
        self._screen.blit(title, (title_x, 20))

        # Títulos dos tabuleiros com ícones
        board_font = pygame.font.Font(None, 36)

        # Título do tabuleiro do jogador
        player_title = board_font.render("Seu Tabuleiro", True, (100, 255, 100))
        self._screen.blit(player_title, (self._player_offset_x, 100))

        # Título do tabuleiro inimigo
        enemy_title = board_font.render("Tabuleiro Inimigo", True, (255, 100, 100))
        self._screen.blit(enemy_title, (self._enemy_offset_x, 100))

        # Desenha tabuleiros
        self._draw_board(
            self._player.board,
            self._player_offset_x,
            self._offset_y,
            show_ships=True,
        )
        self._draw_board(
            self._computer.board,
            self._enemy_offset_x,
            self._offset_y,
            show_ships=False,
        )

        # Caixa de mensagem de status
        message_box = pygame.Rect(50, self._height - 120, self._width - 100, 80)
        message_surface = pygame.Surface((self._width - 100, 80), pygame.SRCALPHA)
        message_surface.fill((0, 0, 0, 200))
        self._screen.blit(message_surface, (message_box.x, message_box.y))
        pygame.draw.rect(self._screen, (255, 215, 0), message_box, 3, border_radius=8)

        # Texto da mensagem
        message_font = pygame.font.Font(None, 32)
        message_text = message_font.render(self._message, True, (255, 255, 255))
        self._screen.blit(message_text, (message_box.x + 20, message_box.y + 15))

        # Informações dos navios
        self._draw_stats()

        # Botão de retorno com efeito hover
        mouse_pos = pygame.mouse.get_pos()
        button = self._return_button
        rect = button["rect"]

        if rect.collidepoint(mouse_pos):
            color = button["hover_color"]
            # Sombra ao passar mouse
            shadow_rect = rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self._screen, (0, 0, 0, 128), shadow_rect, border_radius=8)
        else:
            color = button["color"]

        pygame.draw.rect(self._screen, color, rect, border_radius=8)
        pygame.draw.rect(self._screen, (255, 255, 255), rect, 3, border_radius=8)

        button_font = pygame.font.Font(None, 36)
        text_surf = button_font.render(button["text"], True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self._screen.blit(text_surf, text_rect)

        pygame.display.flip()

    def _draw_board(self, board, offset_x, offset_y, show_ships=True):
        """Desenha um tabuleiro na tela"""
        size = board.size

        # Determina se este tabuleiro está ativo
        is_player_board = board == self._player.board
        is_active = False
        glow_color = (255, 215, 0)  # Dourado

        if is_player_board:
            # Tabuleiro do jogador está ativo quando é turno do computador (sendo atacado)
            if not self._controller.is_player_turn() or self._waiting_computer:
                is_active = True
                glow_color = (255, 100, 100)  # Vermelho (sob ataque)
        else:
            # Tabuleiro inimigo está ativo quando é turno do jogador (pode atacar)
            if self._controller.is_player_turn() and not self._waiting_computer:
                is_active = True
                glow_color = (100, 255, 100)  # Verde (pode atacar)

        # Desenha fundo do tabuleiro
        board_bg = pygame.Rect(
            offset_x - 10,
            offset_y - 10,
            size * self._cell_size + 20,
            size * self._cell_size + 20,
        )
        bg_surface = pygame.Surface((board_bg.width, board_bg.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self._screen.blit(bg_surface, (board_bg.x, board_bg.y))

        # Desenha borda com efeito de brilho se ativo
        if is_active:
            # Brilho externo
            for i in range(3):
                alpha = int(self._glow_alpha * (1 - i * 0.3))
                glow_rect = board_bg.inflate(i * 6, i * 6)
                glow_surface = pygame.Surface(
                    (glow_rect.width, glow_rect.height), pygame.SRCALPHA
                )
                r, g, b = glow_color
                pygame.draw.rect(
                    glow_surface,
                    (r, g, b, alpha),
                    pygame.Rect(0, 0, glow_rect.width, glow_rect.height),
                    6 - i * 2,
                    border_radius=10 + i * 2,
                )
                self._screen.blit(glow_surface, (glow_rect.x, glow_rect.y))

            # Borda principal (mais brilhante)
            pygame.draw.rect(self._screen, glow_color, board_bg, 4, border_radius=10)
        else:
            # Borda normal
            pygame.draw.rect(self._screen, (139, 0, 0), board_bg, 4, border_radius=10)

        # Desenha células
        for row in range(size):
            for col in range(size):
                x = offset_x + col * self._cell_size
                y = offset_y + row * self._cell_size
                rect = pygame.Rect(x, y, self._cell_size, self._cell_size)

                cell = board.grid[row][col]

                # Background color with transparency
                if cell == "~":
                    color = (0, 119, 190, 150)
                elif cell == "N" and show_ships:
                    color = (100, 100, 100, 200)
                elif cell == "N" and not show_ships:
                    color = (0, 119, 190, 150)
                elif cell == "X":
                    color = (220, 20, 60, 200)
                elif cell == "O":
                    color = (200, 200, 200, 150)
                else:
                    color = (0, 119, 190, 150)

                cell_surface = pygame.Surface(
                    (self._cell_size, self._cell_size), pygame.SRCALPHA
                )
                cell_surface.fill(color)
                self._screen.blit(cell_surface, (x, y))
                pygame.draw.rect(self._screen, (255, 255, 255, 100), rect, 1)

        # Draw ship images if showing ships
        if show_ships:
            for ship in board.ships:
                # Sort positions by visual order
                # For horizontal ships: sort by column (left to right)
                # For vertical ships: sort by row (top to bottom)
                if ship.horizontal:
                    sorted_positions = sorted(ship.positions, key=lambda p: p[1])
                else:
                    sorted_positions = sorted(ship.positions, key=lambda p: p[0])

                # Draw each segment with corresponding image index
                for i, pos in enumerate(sorted_positions):
                    ship_row, ship_col = pos
                    x = offset_x + ship_col * self._cell_size
                    y = offset_y + ship_row * self._cell_size

                    # Check if this position is hit
                    is_hit = pos in ship.hits

                    # Get ship image for this segment (i is the correct index)
                    img = ship.get_image(i, self._cell_size)
                    if img and not is_hit:
                        self._screen.blit(img, (x, y))

        # Draw hit/miss images (permanent)
        for row in range(size):
            for col in range(size):
                x = offset_x + col * self._cell_size
                y = offset_y + row * self._cell_size
                cell = board.grid[row][col]

                # Draw images instead of symbols
                if cell == "X":
                    # Hit - draw hit image
                    if "hit" in self._bomb_images:
                        img = pygame.transform.scale(
                            self._bomb_images["hit"], (self._cell_size, self._cell_size)
                        )
                        self._screen.blit(img, (x, y))
                elif cell == "O":
                    # Miss - draw miss image
                    if "miss" in self._bomb_images:
                        img = pygame.transform.scale(
                            self._bomb_images["miss"],
                            (self._cell_size, self._cell_size),
                        )
                        self._screen.blit(img, (x, y))

        # Draw bomb animation if active (only shows during animation)
        self._draw_bomb_animation(board, offset_x, offset_y)

    def _draw_bomb_animation(self, board, offset_x, offset_y):
        """Desenha animação de bomba sobre as células"""
        if not self._bomb_animation:
            return

        # Verifica se esta animação é para este tabuleiro
        is_player_board = board == self._player.board
        target_board = "player" if is_player_board else "enemy"

        if self._bomb_animation["board"] != target_board:
            return

        row = self._bomb_animation["row"]
        col = self._bomb_animation["col"]
        stage = self._bomb_animation["stage"]

        x = offset_x + col * self._cell_size
        y = offset_y + row * self._cell_size

        # Seleciona imagem baseada no estágio
        if stage == "bomb":
            img_key = "bomb"
        elif stage == "hit":
            img_key = "hit"
        else:  # miss
            img_key = "miss"

        # Desenha a imagem
        if img_key in self._bomb_images:
            img = pygame.transform.scale(
                self._bomb_images[img_key], (self._cell_size, self._cell_size)
            )
            self._screen.blit(img, (x, y))

    def _draw_stats(self):
        """Desenha informações sobre navios restantes"""
        # Obtém status do jogo do controlador
        status = self._controller.get_game_status()

        # Info boxes
        info_y = self._height - 180

        # Player ships info box
        player_box = pygame.Rect(50, info_y, 300, 50)
        player_surface = pygame.Surface((300, 50), pygame.SRCALPHA)
        player_surface.fill((0, 100, 0, 200))
        self._screen.blit(player_surface, (player_box.x, player_box.y))
        pygame.draw.rect(self._screen, (100, 255, 100), player_box, 3, border_radius=8)

        font = pygame.font.Font(None, 28)
        player_text = font.render(
            f"Seus navios: {status['player_ships_remaining']}/{status['player_ships_total']}",
            True,
            (255, 255, 255),
        )
        self._screen.blit(player_text, (player_box.x + 15, player_box.y + 13))

        # Enemy ships info box
        enemy_box = pygame.Rect(370, info_y, 330, 50)
        enemy_surface = pygame.Surface((330, 50), pygame.SRCALPHA)
        enemy_surface.fill((100, 0, 0, 200))
        self._screen.blit(enemy_surface, (enemy_box.x, enemy_box.y))
        pygame.draw.rect(self._screen, (255, 100, 100), enemy_box, 3, border_radius=8)

        enemy_text = font.render(
            f"Navios inimigos: {status['computer_ships_remaining']}/{status['computer_ships_total']}",
            True,
            (255, 255, 255),
        )
        self._screen.blit(enemy_text, (enemy_box.x + 15, enemy_box.y + 13))

    def check_click(self, pos):
        """Processa clique do mouse"""
        # Se o jogo terminou, vai para tela de game over
        if self._controller.finished:
            return self._get_game_over_data()

        # Verifica botão de retorno
        if self._return_button["rect"].collidepoint(pos):
            # Toca som de clique
            if self._click_sound:
                self._click_sound.play()
            return "home"

        # Se esperando computador, ignora cliques no tabuleiro
        if self._waiting_computer:
            return None

        # Verifica clique no tabuleiro inimigo
        x, y = pos
        if (
            self._enemy_offset_x <= x < self._enemy_offset_x + 10 * self._cell_size
            and self._offset_y <= y < self._offset_y + 10 * self._cell_size
        ):
            col = (x - self._enemy_offset_x) // self._cell_size
            row = (y - self._offset_y) // self._cell_size

            self._process_player_attack(row, col)

        return None

    def handle_event(self, event):
        """Trata eventos e verifica game over"""
        # Verifica se game over está pendente (definido por update quando jogo termina)
        if self._game_over_pending or self._controller.finished:
            return self._get_game_over_data()

        # Trata cliques do mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.check_click(event.pos)

        return None

    def _process_player_attack(self, row, col):
        """Processa ataque do jogador usando controlador"""
        # Verifica se já atacou
        if self._computer.board.grid[row][col] in ["X", "O"]:
            self._message = "Você já atacou esta posição!"
            return

        # Inicia animação de bomba
        current_time = pygame.time.get_ticks()
        self._bomb_animation = {
            "row": row,
            "col": col,
            "board": "enemy",
            "stage": "bomb",
            "time": current_time,
            "result": None,  # Será definido após animação
        }

        # Armazena dados do ataque para processamento posterior
        self._pending_attack = {"row": row, "col": col, "time": current_time}

    def _complete_player_attack(self):
        """Completa ataque do jogador após animação"""
        if not self._pending_attack:
            return

        row = self._pending_attack["row"]
        col = self._pending_attack["col"]

        result, ship_destroyed, game_over, message = (
            self._controller.process_player_attack(row, col)
        )

        self._message = message
        self._pending_attack = None

        if game_over:
            self._save_ranking()
            self._bomb_animation = None
            self._game_over_pending = True  # Sinaliza para navegar no próximo evento
            return

        # Turno do computador (somente se jogo não acabou)
        if not game_over:
            self._controller.switch_turn()
            self._waiting_computer = True
            self._waiting_computer_time = (
                pygame.time.get_ticks() + 1500
            )  # Atraso de 1.5s

    def update(self):
        """Atualiza estado do jogo (chamado no loop principal)"""
        # Atualiza tela base (animação de fundo)
        super().update()

        current_time = pygame.time.get_ticks()

        # Processamento da animação de bomba
        if self._bomb_animation:
            time_elapsed = current_time - self._bomb_animation["time"]

            if self._bomb_animation["stage"] == "bomb":
                # Mostra bomba por uma duração
                if time_elapsed >= self._bomb_animation_duration:
                    # Processa o ataque e determina resultado
                    row = self._bomb_animation["row"]
                    col = self._bomb_animation["col"]

                    # Verifica o que está na célula
                    if self._bomb_animation["board"] == "enemy":
                        cell = self._computer.board.grid[row][col]
                    else:
                        cell = self._player.board.grid[row][col]

                    # Determina se acertou ou errou
                    is_hit = cell == "N"

                    # Toca som apropriado
                    if is_hit and self._hit_sound:
                        self._hit_sound.play()
                    elif not is_hit and self._miss_sound:
                        self._miss_sound.play()

                    # Atualiza estágio da animação
                    self._bomb_animation["stage"] = "hit" if is_hit else "miss"
                    self._bomb_animation["time"] = current_time

                    # Completa o ataque
                    if self._bomb_animation["board"] == "enemy":
                        self._complete_player_attack()

            elif self._bomb_animation["stage"] in ["hit", "miss"]:
                # Mostra resultado acerto/erro por uma duração
                if time_elapsed >= self._result_animation_duration:
                    self._bomb_animation = None

        # Animação de brilho (efeito pulsante para tabuleiro ativo)
        if current_time - self._glow_last_update >= self._glow_update_interval:
            self._glow_alpha += self._glow_direction
            if self._glow_alpha >= 200:
                self._glow_direction = -5
            elif self._glow_alpha <= 50:
                self._glow_direction = 5
            self._glow_last_update = current_time

        # Processamento do turno do computador
        if (
            self._waiting_computer
            and pygame.time.get_ticks() >= self._waiting_computer_time
        ):
            self._process_computer_turn()

    def _process_computer_turn(self):
        """Processa turno do computador usando controlador"""
        result, ship_destroyed, game_over, message = (
            self._controller.process_computer_attack()
        )

        # Toca som apropriado baseado no resultado
        if result == "hit" and self._hit_sound:
            self._hit_sound.play()
        elif result == "miss" and self._miss_sound:
            self._miss_sound.play()

        self._message = message

        if game_over:
            self._waiting_computer = False
            self._save_ranking()
            self._game_over_pending = True  # Sinaliza para navegar no próximo evento
            return

        # Volta para turno do jogador
        self._controller.switch_turn()
        self._waiting_computer = False
        if not self._controller.finished:
            self._message += " | Seu turno!"

    def _save_ranking(self):
        """Salva resultado da partida no sistema de ranking"""
        if self._ranking_saved or not self._ranking_controller:
            return

        # Obtém estatísticas do jogo
        status = self._controller.get_game_status()

        # Determina nome do jogador
        player_name = self._current_user if self._current_user else self._player.name

        # Determina se jogador venceu
        won = self._controller.winner == self._player

        # Obtém estatísticas da partida
        turns = status["turn"]
        # Conta quantos navios PRÓPRIOS sobreviveram (não os destruídos do oponente)
        ships_remaining = status["player_ships_remaining"]

        # Calcula precisão (acertos / total de ataques)
        if won:
            attacks = self._computer.board.attacks
            board = self._computer.board
        else:
            attacks = self._player.board.attacks
            board = self._player.board

        total_attacks = len(attacks)
        hits = sum(1 for pos in attacks if board.grid[pos[0]][pos[1]] == "X")
        accuracy = hits / total_attacks if total_attacks > 0 else 0.0

        # Salva no ranking
        try:
            self._ranking_controller.add_match_result(
                player_name=player_name,
                won=won,
                turns=turns,
                ships_remaining=ships_remaining,
                accuracy=accuracy,
            )
            self._ranking_saved = True
            print(f"Ranking salvo: {player_name} - {'VITÓRIA' if won else 'DERROTA'}")
        except Exception as e:
            print(f"Erro ao salvar ranking: {e}")

    def _get_game_over_data(self):
        """Obtém dados para tela de game over"""
        status = self._controller.get_game_status()
        player_name = self._current_user if self._current_user else self._player.name
        won = self._controller.winner == self._player

        # Obtém estatísticas da partida
        turns = status["turn"]
        # Conta quantos navios PRÓPRIOS sobreviveram
        ships_remaining = status["player_ships_remaining"]

        if won:
            attacks = self._computer.board.attacks
            board = self._computer.board
        else:
            attacks = self._player.board.attacks
            board = self._player.board

        # Calcula precisão
        total_attacks = len(attacks)
        hits = sum(1 for pos in attacks if board.grid[pos[0]][pos[1]] == "X")
        accuracy = hits / total_attacks if total_attacks > 0 else 0.0

        # Calcula pontuação se ranking está habilitado
        score = None
        if self._ranking_controller:
            score = self._ranking_controller._calculate_score(
                won, turns, ships_remaining, accuracy
            )

        stats = {
            "player_name": player_name,
            "turns": turns,
            "ships_remaining": ships_remaining,
            "accuracy": accuracy,
            "score": score,
        }

        return ("game_over", (won, stats))
