"""Scoops Ahoy Ship - navio temático de 4 células (Encouraçado)"""

from model.entities.ship import Ship


class ScoopsAhoyShip(Ship):
    """Navio temático baseado na sorveteria Scoops Ahoy (4 células)"""

    def __init__(self):
        super().__init__(
            name="Scoops Ahoy", size=3, image_path="src/assets/ships/scoops_ahoy"
        )
