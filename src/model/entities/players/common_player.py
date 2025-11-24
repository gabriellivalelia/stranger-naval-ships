"""CommonPlayer - Human player"""

import random

from model.entities.player import Player
from model.entities.ships import (
    ArgylesVanShip,
    ChristmasShip,
    DemogorgonShip,
    LaboratoryShip,
    ScoopsAhoyShip,
)


class CommonPlayer(Player):
    """Human player that interacts via interface"""

    def __init__(self, name="Player"):
        super().__init__(name)

    def place_ships(self):
        """
        Posiciona os navios do jogador no tabuleiro aleatoriamente.
        Usa posicionamento automático aleatório para navios temáticos.
        """
        default_ships = [
            DemogorgonShip(),  # 5 células
            ScoopsAhoyShip(),  # 4 células
            ChristmasShip(),  # 3 células
            ArgylesVanShip(),  # 3 células
            LaboratoryShip(),  # 2 células
        ]

        # Random positioning
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
        Jogador humano não faz ataques automáticos.
        Ataque é feito através da interface.
        """
        pass
