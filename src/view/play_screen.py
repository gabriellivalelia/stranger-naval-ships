import pygame

from controller.play_controller import PlayController
from view.base_screen import BaseScreen


class PlayScreen(BaseScreen):
    def __init__(self, player=None, ranking_controller=None, current_user=None):
        super().__init__("Jogo - Batalha Naval")

        # Colors
        self.BG_COLOR = (20, 30, 50)
        self.WATER_COLOR = (0, 119, 190)
        self.SHIP_COLOR = (100, 100, 100)
        self.HIT_COLOR = (220, 20, 60)
        self.MISS_COLOR = (255, 255, 255)
        self.GRID_COLOR = (50, 50, 80)
        self.TEXT_COLOR = (255, 255, 255)

        # Grid configuration
        self.cell_size = 50
        self.player_offset_x = 50
        self.offset_y = 100
        self.enemy_offset_x = 750

        # Initialize game controller
        self.controller = PlayController(player=player)
        self.player = self.controller.player
        self.computer = self.controller.computer

        # Ranking system
        self.ranking_controller = ranking_controller
        self.current_user = current_user
        self.ranking_saved = False  # Flag to save ranking only once

        # Game state
        self.message = "Seu turno! Clique no tabuleiro inimigo para atacar"
        self.waiting_computer = False
        self.waiting_computer_time = 0

        # Return button
        self.return_button = pygame.Rect(self.width - 150, 20, 130, 40)

    def draw(self):
        self.screen.fill(self.BG_COLOR)

        # Titles
        title_font = pygame.font.Font(None, 36)
        player_title = title_font.render("Seu Tabuleiro", True, self.TEXT_COLOR)
        enemy_title = title_font.render("Tabuleiro Inimigo", True, self.TEXT_COLOR)
        self.screen.blit(player_title, (self.player_offset_x, 50))
        self.screen.blit(enemy_title, (self.enemy_offset_x, 50))

        # Draw boards
        self._draw_board(
            self.player.board,
            self.player_offset_x,
            self.offset_y,
            show_ships=True,
        )
        self._draw_board(
            self.computer.board,
            self.enemy_offset_x,
            self.offset_y,
            show_ships=False,
        )

        # Status message
        message_font = pygame.font.Font(None, 28)
        message_text = message_font.render(self.message, True, self.TEXT_COLOR)
        self.screen.blit(message_text, (50, self.height - 80))

        # Ship info
        self._draw_ship_info()

        # Return button
        pygame.draw.rect(
            self.screen, (200, 50, 50), self.return_button, border_radius=5
        )
        button_font = pygame.font.Font(None, 28)
        button_text = button_font.render("Voltar", True, self.TEXT_COLOR)
        self.screen.blit(
            button_text, (self.return_button.x + 30, self.return_button.y + 8)
        )

        pygame.display.flip()

    def _draw_board(self, board, offset_x, offset_y, show_ships=True):
        """Draws a board on the screen"""
        size = board.size

        # Draw cells
        for row in range(size):
            for col in range(size):
                x = offset_x + col * self.cell_size
                y = offset_y + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                cell = board.grid[row][col]

                # Background color
                if cell == "~":
                    color = self.WATER_COLOR
                elif cell == "N" and show_ships:
                    color = self.SHIP_COLOR
                elif cell == "N" and not show_ships:
                    color = self.WATER_COLOR
                elif cell == "X":
                    color = self.HIT_COLOR
                elif cell == "O":
                    color = self.MISS_COLOR
                else:
                    color = self.WATER_COLOR

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)

                # Draw symbols
                if cell == "X":
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (x + 10, y + 10),
                        (x + self.cell_size - 10, y + self.cell_size - 10),
                        3,
                    )
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (x + self.cell_size - 10, y + 10),
                        (x + 10, y + self.cell_size - 10),
                        3,
                    )
                elif cell == "O":
                    pygame.draw.circle(
                        self.screen,
                        self.GRID_COLOR,
                        (x + self.cell_size // 2, y + self.cell_size // 2),
                        15,
                        3,
                    )

    def _draw_ship_info(self):
        """Draws information about remaining ships"""
        font = pygame.font.Font(None, 24)
        y_pos = self.height - 150

        # Get game status from controller
        status = self.controller.get_game_status()

        # Player ships
        text = font.render(
            f"Seus navios: {status['player_ships_remaining']}/{status['player_ships_total']}",
            True,
            self.TEXT_COLOR,
        )
        self.screen.blit(text, (50, y_pos))

        # Enemy ships
        text = font.render(
            f"Navios inimigos: {status['computer_ships_remaining']}/{status['computer_ships_total']}",
            True,
            self.TEXT_COLOR,
        )
        self.screen.blit(text, (50, y_pos + 30))

    def check_click(self, pos):
        """Process mouse click"""
        # If game is finished, go to game over screen
        if self.controller.finished:
            return self._get_game_over_data()

        # Check return button
        if self.return_button.collidepoint(pos):
            return "home"

        # If waiting for computer, ignore board clicks
        if self.waiting_computer:
            return None

        # Check click on enemy board
        x, y = pos
        if (
            self.enemy_offset_x <= x < self.enemy_offset_x + 10 * self.cell_size
            and self.offset_y <= y < self.offset_y + 10 * self.cell_size
        ):
            col = (x - self.enemy_offset_x) // self.cell_size
            row = (y - self.offset_y) // self.cell_size

            self._process_player_attack(row, col)

        return None

    def _process_player_attack(self, row, col):
        """Process player attack using controller"""
        result, ship_destroyed, game_over, message = (
            self.controller.process_player_attack(row, col)
        )

        self.message = message

        if result == "ja_atacado":
            return

        if game_over:
            self._save_ranking()
            # Don't return here, let check_click handle the navigation

        # Computer's turn (only if game is not over)
        if not game_over:
            self.controller.switch_turn()
            self.waiting_computer = True
            self.waiting_computer_time = pygame.time.get_ticks() + 500  # 0.5s delay

    def update(self):
        """Update game state (called in main loop)"""
        if (
            self.waiting_computer
            and pygame.time.get_ticks() >= self.waiting_computer_time
        ):
            self._process_computer_turn()

    def _process_computer_turn(self):
        """Process computer turn using controller"""
        result, ship_destroyed, game_over, message = (
            self.controller.process_computer_attack()
        )

        self.message = message

        if game_over:
            self.waiting_computer = False
            self._save_ranking()
            return

        # Back to player's turn
        self.controller.switch_turn()
        self.waiting_computer = False
        if not self.controller.finished:
            self.message += " | Seu turno!"

    def _save_ranking(self):
        """Save match result to ranking system"""
        if self.ranking_saved or not self.ranking_controller:
            return

        # Get game statistics
        status = self.controller.get_game_status()

        # Determine player name
        player_name = self.current_user if self.current_user else self.player.name

        # Determine if player won
        won = self.controller.winner == self.player

        # Get match statistics
        turns = status["turn"]
        if won:
            ships_destroyed = (
                status["computer_ships_total"] - status["computer_ships_remaining"]
            )
        else:
            ships_destroyed = (
                status["player_ships_total"] - status["player_ships_remaining"]
            )

        # Calculate accuracy (hits / total attacks)
        if won:
            attacks = self.computer.board.attacks
            board = self.computer.board
        else:
            attacks = self.player.board.attacks
            board = self.player.board

        total_attacks = len(attacks)
        hits = sum(1 for pos in attacks if board.grid[pos[0]][pos[1]] == "X")
        accuracy = hits / total_attacks if total_attacks > 0 else 0.0

        # Save to ranking
        try:
            self.ranking_controller.add_match_result(
                player_name=player_name,
                won=won,
                turns=turns,
                ships_destroyed=ships_destroyed,
                accuracy=accuracy,
            )
            self.ranking_saved = True
            print(f"✅ Ranking saved: {player_name} - {'WON' if won else 'LOST'}")
        except Exception as e:
            print(f"❌ Error saving ranking: {e}")

    def _get_game_over_data(self):
        """Get data for game over screen"""
        status = self.controller.get_game_status()
        player_name = self.current_user if self.current_user else self.player.name
        won = self.controller.winner == self.player

        # Get match statistics
        turns = status["turn"]
        if won:
            ships_destroyed = (
                status["computer_ships_total"] - status["computer_ships_remaining"]
            )
            attacks = self.computer.board.attacks
            board = self.computer.board
        else:
            ships_destroyed = (
                status["player_ships_total"] - status["player_ships_remaining"]
            )
            attacks = self.player.board.attacks
            board = self.player.board

        # Calculate accuracy
        total_attacks = len(attacks)
        hits = sum(1 for pos in attacks if board.grid[pos[0]][pos[1]] == "X")
        accuracy = hits / total_attacks if total_attacks > 0 else 0.0

        # Calculate score if ranking is enabled
        score = None
        if self.ranking_controller:
            from controller.ranking_controller import RankingController

            temp_controller = RankingController()
            score = temp_controller._calculate_score(
                won, turns, ships_destroyed, accuracy
            )

        stats = {
            "player_name": player_name,
            "turns": turns,
            "ships_destroyed": ships_destroyed,
            "accuracy": accuracy,
            "score": score,
        }

        return ("game_over", (won, stats))
