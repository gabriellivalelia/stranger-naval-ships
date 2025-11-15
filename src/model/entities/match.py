"""Classe Match - gerencia uma partida de batalha naval"""


class Match:
    """Gerencia uma partida entre dois jogadores"""

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.turn = 0
        self.winner = None
        self.history = []  # Game history

    def switch_player(self):
        """Switches between player 1 and player 2"""
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1
        self.turn += 1

    def get_opponent(self):
        """Returns the opponent of the current player"""
        if self.current_player == self.player1:
            return self.player2
        return self.player1

    def process_turn(self, row, col):
        """
        Processes a game turn.
        Returns: (result, ship_destroyed, game_over)
        """
        opponent = self.get_opponent()
        result, ship = opponent.board.receive_attack(row, col)

        # Record in history
        self.history.append(
            {
                "turn": self.turn,
                "player": self.current_player.name,
                "position": (row, col),
                "result": result,
            }
        )

        # Check if ship was destroyed
        ship_destroyed = ship.is_destroyed() if ship else False

        # Check game over
        game_over = opponent.has_lost()
        if game_over:
            self.winner = self.current_player

        return (result, ship_destroyed, game_over)

    def start(self):
        """Prepares the match to start"""
        # Only place ships if players don't have ships yet
        if not self.player1.board.ships:
            self.player1.place_ships()
        if not self.player2.board.ships:
            self.player2.place_ships()
        self.current_player = self.player1

    def get_status(self):
        """Returns information about the current match state"""
        return {
            "turn": self.turn,
            "current_player": self.current_player.name,
            "ships_p1": len(
                [s for s in self.player1.board.ships if not s.is_destroyed()]
            ),
            "ships_p2": len(
                [s for s in self.player2.board.ships if not s.is_destroyed()]
            ),
            "winner": self.winner.name if self.winner else None,
        }
