"""RankingRepository - Interface abstrata para persistência de rankings"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class RankingRepository(ABC):
    """Interface para repositórios de ranking"""

    @abstractmethod
    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Cria um novo usuário no sistema.

        Args:
            username: Nome do usuário
            password: Senha do usuário

        Returns:
            Tupla (sucesso, mensagem)
        """
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Autentica um usuário.

        Args:
            username: Nome do usuário
            password: Senha do usuário

        Returns:
            Tupla (sucesso, mensagem)
        """
        pass

    @abstractmethod
    def add_score(
        self,
        username: str,
        won: bool,
        turns: int,
        ships_remaining: int,
        accuracy: float,
        score: int,
    ) -> bool:
        """
        Adiciona um resultado de partida ao ranking.

        Args:
            username: Nome do jogador
            won: True se o jogador venceu
            turns: Número de turnos da partida
            ships_remaining: Número de navios próprios que sobreviveram
            accuracy: Precisão dos ataques (0.0 a 1.0)
            score: Pontuação calculada

        Returns:
            True se salvou com sucesso
        """
        pass

    @abstractmethod
    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """
        Retorna os melhores resultados ordenados por pontuação.

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de resultados ordenada por score
        """
        pass

    @abstractmethod
    def get_user_stats(self, username: str) -> Optional[Dict]:
        """
        Retorna estatísticas de um jogador específico.

        Args:
            username: Nome do jogador

        Returns:
            Dicionário com estatísticas ou None se não houver dados
        """
        pass

    @abstractmethod
    def clear_all(self) -> bool:
        """
        Limpa todos os rankings.

        Returns:
            True se limpou com sucesso
        """
        pass
