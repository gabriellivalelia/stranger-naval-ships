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
        # Initialize players
        if player:
            self.player = player
        else:
            self.player = CommonPlayer("You")
            self.player.place_ships()

        self.computer = SystemPlayer("Computer")
        self.computer.place_ships()  # Always place computer's ships

        # Initialize match
        self.match = Match(self.player, self.computer)
        self.match.start()

        # Game state
        self.finished = False
        self.winner = None

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
        if self.finished:
            return ("already_attacked", False, True, "The game is already over!")

        result, ship_destroyed, game_over = self.match.process_turn(row, col)

        # Generate message
        if result == "already_attacked":
            message = "You already attacked this position!"
        elif result == "hit":
            if ship_destroyed:
                message = "HIT and DESTROYED an enemy ship!"
            else:
                message = "HIT! Keep attacking!"
        else:
            message = "WATER! You missed..."

        if game_over:
            self.finished = True
            self.winner = self.player
            message = "🎉 YOU WON! Destroyed all enemy ships!"

        return (result, ship_destroyed, game_over, message)

    def process_computer_attack(self) -> Tuple[str, bool, bool, Optional[str]]:
        """
        Processes a computer attack.

        Returns:
            Tuple with (result, ship_destroyed, game_over, message)
        """
        if self.finished:
            return ("already_attacked", False, True, "The game is already over!")

        attack = self.computer.make_attack()
        if not attack:
            return ("water", False, False, "Computer couldn't attack!")

        row, col = attack
        result, ship_destroyed, game_over = self.match.process_turn(row, col)

        # Record result so the computer can learn
        self.computer.record_attack_result((row, col), result, ship_destroyed)

        # Generate message
        if result == "hit":
            if ship_destroyed:
                message = f"💥 Enemy HIT ({row},{col}) and DESTROYED your ship!"
            else:
                message = f"💥 Enemy HIT ({row},{col})!"
        else:
            message = f"Enemy missed at ({row},{col}). Your turn!"

        if game_over:
            self.finished = True
            self.winner = self.computer
            message = "😢 YOU LOST! The enemy destroyed all your ships!"

        return (result, ship_destroyed, game_over, message)

    def switch_turn(self):
        """Switches turn between players"""
        self.match.switch_player()

    def is_player_turn(self) -> bool:
        """Checks if it's the player's turn"""
        return self.match.current_player == self.player

    def get_game_status(self) -> dict:
        """
        Returns information about the current game state.

        Returns:
            Dictionary with match statistics
        """
        player_ships = [
            ship for ship in self.player.board.ships if not ship.is_destroyed()
        ]
        computer_ships = [
            ship for ship in self.computer.board.ships if not ship.is_destroyed()
        ]

        return {
            "turn": self.match.turn,
            "current_player": self.match.current_player.name,
            "player_ships_remaining": len(player_ships),
            "player_ships_total": len(self.player.board.ships),
            "computer_ships_remaining": len(computer_ships),
            "computer_ships_total": len(self.computer.board.ships),
            "finished": self.finished,
            "winner": self.winner.name if self.winner else None,
        }

    def is_valid_attack_position(self, row: int, col: int) -> bool:
        """
        Checks if a position is valid for attack.

        Args:
            row: Row (0-9)
            col: Column (0-9)

        Returns:
            True if the position is valid and hasn't been attacked yet
        """
        if row < 0 or row >= 10 or col < 0 or col >= 10:
            return False

        return (row, col) not in self.computer.board.attacks
