"""Classe Player - classe base para jogadores"""

from abc import ABC, abstractmethod

from model.entities.board import Board


class Player(ABC):
    """Classe base para jogadores (humano ou computador)"""

    def __init__(self, name):
        self._name = name
        self._board = Board()

    @abstractmethod
    def make_attack(self):
        """Método abstrato - deve ser implementado por subclasses"""
        raise NotImplementedError("Subclasses devem implementar make_attack()")

    @abstractmethod
    def place_ships(self):
        """Método abstrato - deve ser implementado por subclasses"""
        raise NotImplementedError("Subclasses devem implementar place_ships()")

    def has_lost(self):
        """Verifica se o jogador perdeu (todos os navios destruídos)"""
        return self._board.all_ships_destroyed()

    @property
    def name(self) -> str:
        """Obtém nome do jogador."""
        return self._name

    @property
    def board(self) -> Board:
        """Obtém tabuleiro do jogador."""
        return self._board

    @board.setter
    def board(self, value: Board):
        """Define tabuleiro do jogador."""
        self._board = value
