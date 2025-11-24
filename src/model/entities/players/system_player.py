"""SystemPlayer - AI-controlled player (computer)"""

import random

from model.entities.player import Player
from model.entities.ships import (
    ArgylesVanShip,
    ChristmasShip,
    DemogorgonShip,
    LaboratoryShip,
    ScoopsAhoyShip,
)


class SystemPlayer(Player):
    """Computer-controlled player with simple AI"""

    def __init__(self, name="Computer"):
        super().__init__(name)
        self._attacked_positions = set()
        self._search_mode = False  # Active search mode after hit
        self._last_hit = None
        self._directions_to_test = []

    def place_ships(self):
        """Posiciona navios aleatoriamente no tabuleiro usando navios temáticos"""
        default_ships = [
            DemogorgonShip(),  # 5 cells
            ScoopsAhoyShip(),  # 4 cells
            ChristmasShip(),  # 3 cells
            ArgylesVanShip(),  # 3 cells
            LaboratoryShip(),  # 2 cells
        ]

        for ship in default_ships:
            placed = False
            attempts = 0
            max_attempts = 100

            while not placed and attempts < max_attempts:
                row = random.randint(0, self._board.size - 1)
                col = random.randint(0, self._board.size - 1)
                horizontal = random.choice([True, False])

                try:
                    self._board.add_ship(ship, row, col, horizontal)
                    placed = True
                except ValueError:
                    attempts += 1

            if not placed:
                print(
                    f"Aviso: Não foi possível posicionar {ship.name} após {max_attempts} tentativas"
                )

    def make_attack(self):
        """
        IA para escolher a próxima posição de ataque.
        Usa estratégia simples: ataque aleatório até acertar, então busca ao redor.
        """
        # If in search mode (hit a ship but didn't destroy it)
        if self._search_mode and self._last_hit:
            attack = self._smart_attack()
            if attack:
                return attack
            else:
                # If no more directions, return to random
                self._search_mode = False

        # Random attack
        return self._random_attack()

    def _random_attack(self):
        """Escolhe uma posição aleatória que ainda não foi atacada"""
        size = self._board.size  # Use own board size (same as opponent's)
        available_positions = []

        for row in range(size):
            for col in range(size):
                if (row, col) not in self._attacked_positions:
                    available_positions.append((row, col))

        if available_positions:
            return random.choice(available_positions)
        return None

    def _smart_attack(self):
        """Ataca posições adjacentes ao último acerto"""
        if not self._last_hit:
            return None

        row, col = self._last_hit
        size = self._board.size  # Use own board size (same as opponent's)

        # Directions: up, down, left, right
        directions = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]

        # Filter valid and unattacked positions
        valid_positions = [
            (r, c)
            for r, c in directions
            if 0 <= r < size
            and 0 <= c < size
            and (r, c) not in self._attacked_positions
        ]

        if valid_positions:
            return random.choice(valid_positions)
        return None

    def record_attack_result(self, position, result, ship_destroyed):
        """Registra resultado do ataque para melhorar próximos movimentos"""
        self._attacked_positions.add(position)

        if result == "hit":
            self._last_hit = position
            if not ship_destroyed:
                self._search_mode = True
            else:
                # Ship destroyed, return to random mode
                self._search_mode = False
                self._last_hit = None
