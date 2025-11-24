"""PlayController - gerencia a lógica de uma partida de batalha naval"""

from typing import Optional, Tuple

from model.entities.match import Match
from model.entities.players.common_player import CommonPlayer
from model.entities.players.system_player import SystemPlayer


class PlayController:
    """Controller responsável pela lógica de jogo durante uma partida"""

    def __init__(self, player: Optional[CommonPlayer] = None):
        """
        Inicializa o controller da partida.

        Args:
            player: Jogador humano (opcional). Se None, cria um novo jogador.
        """
        # Inicializa jogadores
        if player:
            self._player = player
        else:
            self._player = CommonPlayer("Você")
            self._player.place_ships()

        self._computer = SystemPlayer("Computador")
        self._computer.place_ships()  # Sempre posiciona navios do computador

        # Inicializa partida
        self._match = Match(self._player, self._computer)
        self._match.start()

        # Estado do jogo
        self._finished = False
        self._winner = None

    def process_player_attack(
        self, row: int, col: int
    ) -> Tuple[str, bool, bool, Optional[str]]:
        """
        Processa um ataque do jogador.

        Args:
            row: Linha do ataque (0-9)
            col: Coluna do ataque (0-9)

        Returns:
            Tupla com (resultado, navio_destruído, jogo_acabou, mensagem)
            - resultado: "acerto", "agua", ou "ja_atacado"
            - navio_destruído: True se destruiu um navio
            - jogo_acabou: True se o jogo acabou
            - mensagem: Mensagem descritiva do resultado
        """
        if self._finished:
            return ("already_attacked", False, True, "O jogo já acabou!")

        result, ship_destroyed, game_over = self._match.process_turn(row, col)

        # Gera mensagem
        if result == "already_attacked":
            message = "Você já atacou esta posição!"
        elif result == "hit":
            if ship_destroyed:
                message = "ACERTOU e DESTRUIU um navio inimigo!"
            else:
                message = "ACERTOU! Continue atacando!"
        else:
            message = "ÁGUA! Você errou..."

        if game_over:
            self._finished = True
            self._winner = self._player
            message = "VOCÊ VENCEU! Destruiu todos os navios inimigos!"

        return (result, ship_destroyed, game_over, message)

    def process_computer_attack(self) -> Tuple[str, bool, bool, Optional[str]]:
        """
        Processa um ataque do computador.

        Returns:
            Tupla com (resultado, navio_destruído, jogo_acabou, mensagem)
        """
        if self._finished:
            return ("already_attacked", False, True, "O jogo já acabou!")

        attack = self._computer.make_attack()
        if not attack:
            return ("water", False, False, "Computador não conseguiu atacar!")

        row, col = attack
        result, ship_destroyed, game_over = self._match.process_turn(row, col)

        # Registra resultado para o computador aprender
        self._computer.record_attack_result((row, col), result, ship_destroyed)

        # Gera mensagem
        if result == "hit":
            if ship_destroyed:
                message = f"Inimigo ACERTOU ({row},{col}) e DESTRUIU seu navio!"
            else:
                message = f"Inimigo ACERTOU ({row},{col})!"
        else:
            message = f"Inimigo errou em ({row},{col}). Sua vez!"

        if game_over:
            self._finished = True
            self._winner = self._computer
            message = "VOCÊ PERDEU! O inimigo destruiu todos os seus navios!"

        return (result, ship_destroyed, game_over, message)

    def switch_turn(self):
        """Alterna turno entre jogadores"""
        self._match.switch_player()

    def is_player_turn(self) -> bool:
        """Verifica se é o turno do jogador"""
        return self._match.current_player == self._player

    def get_game_status(self) -> dict:
        """
        Retorna informações sobre o estado atual do jogo.

        Returns:
            Dicionário com estatísticas da partida
        """
        player_ships = [
            ship for ship in self._player.board.ships if not ship.is_destroyed()
        ]
        computer_ships = [
            ship for ship in self._computer.board.ships if not ship.is_destroyed()
        ]

        return {
            "turn": self._match.turn,
            "current_player": self._match.current_player.name,
            "player_ships_remaining": len(player_ships),
            "player_ships_total": len(self._player.board.ships),
            "computer_ships_remaining": len(computer_ships),
            "computer_ships_total": len(self._computer.board.ships),
            "finished": self._finished,
            "winner": self._winner.name if self._winner else None,
        }

    def is_valid_attack_position(self, row: int, col: int) -> bool:
        """
        Verifica se uma posição é válida para ataque.

        Args:
            row: Linha (0-9)
            col: Coluna (0-9)

        Returns:
            True se a posição é válida e ainda não foi atacada
        """
        if row < 0 or row >= 10 or col < 0 or col >= 10:
            return False

        return (row, col) not in self._computer.board.attacks

    @property
    def player(self) -> CommonPlayer:
        """Retorna o jogador."""
        return self._player

    @property
    def computer(self) -> SystemPlayer:
        """Retorna o computador."""
        return self._computer

    @property
    def finished(self) -> bool:
        """Verifica se o jogo terminou."""
        return self._finished

    @property
    def winner(self):
        """Retorna o vencedor."""
        return self._winner
