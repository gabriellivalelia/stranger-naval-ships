"""Demogorgon Ship - navio temático de 5 células (Porta-Aviões)"""

from model.entities.ship import Ship


class DemogorgonShip(Ship):
    """Navio temático baseado no Demogorgon (4 células - o maior)"""

    def __init__(self):
        super().__init__(
            name="Demogorgon", size=4, image_path="src/assets/ships/demogorgon"
        )
