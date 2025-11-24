"""Classe Match - gerencia uma partida de batalha naval"""


class Match:
    """Gerencia uma partida entre dois jogadores"""

    def __init__(self, player1, player2):
        self._player1 = player1
        self._player2 = player2
        self._current_player = player1
        self._turn = 0
        self._winner = None
        self._history = []  # Histórico da partida

    def switch_player(self):
        """Alterna entre jogador 1 e jogador 2"""
        if self._current_player == self._player1:
            self._current_player = self._player2
        else:
            self._current_player = self._player1
        self._turn += 1

    def get_opponent(self):
        """Retorna o oponente do jogador atual"""
        if self._current_player == self._player1:
            return self._player2
        return self._player1

    def process_turn(self, row, col):
        """
        Processa um turno do jogo.
        Retorna: (result, ship_destroyed, game_over)
        """
        opponent = self.get_opponent()
        result, ship = opponent.board.receive_attack(row, col)

        # Registra no histórico
        self._history.append(
            {
                "turn": self._turn,
                "player": self._current_player.name,
                "position": (row, col),
                "result": result,
            }
        )

        # Verifica se o navio foi destruído
        ship_destroyed = ship.is_destroyed() if ship else False
        print(
            f"[Match] Após ataque em ({row},{col}): result={result}, ship_destroyed={ship_destroyed}"
        )

        # Verifica fim de jogo
        game_over = opponent.has_lost()
        print(f"[Match] game_over={game_over}")
        if game_over:
            self._winner = self._current_player
            print(f"[Match] Vencedor: {self._winner.name}")

        return (result, ship_destroyed, game_over)

    def start(self):
        """Prepara a partida para começar"""
        # Posiciona navios apenas se os jogadores ainda não tiverem navios
        if not self._player1.board.ships:
            self._player1.place_ships()
        if not self._player2.board.ships:
            self._player2.place_ships()
        self._current_player = self._player1

    def get_status(self):
        """Retorna informações sobre o estado atual da partida"""
        return {
            "turn": self._turn,
            "current_player": self._current_player.name,
            "ships_p1": len(
                [s for s in self._player1.board.ships if not s.is_destroyed()]
            ),
            "ships_p2": len(
                [s for s in self._player2.board.ships if not s.is_destroyed()]
            ),
            "winner": self._winner.name if self._winner else None,
        }

    @property
    def player1(self):
        """Obtém jogador 1."""
        return self._player1

    @property
    def player2(self):
        """Obtém jogador 2."""
        return self._player2

    @property
    def current_player(self):
        """Obtém jogador atual."""
        return self._current_player

    @property
    def turn(self) -> int:
        """Obtém número do turno atual."""
        return self._turn

    @property
    def winner(self):
        """Obtém vencedor se o jogo terminou."""
        return self._winner

    @property
    def history(self) -> list:
        """Obtém histórico do jogo."""
        return self._history
