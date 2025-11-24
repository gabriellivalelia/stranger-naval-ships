"""RankingController - controlador facade que delega persistência para um repositório

Este controlador mantém a API usada pelas views e pelo MainController.
Ele escolhe uma implementação apropriada de RankingRepository (Mongo ou JSON)
e expõe um atributo mongo quando um repositório Mongo é usado para que código
existente que chama ranking_controller.mongo.create_user(...) continue funcionando.
"""

from typing import Dict, List, Optional, Tuple

from model.repositories import JsonRankingRepository, MongoRankingRepository
from model.repositories.ranking_repository import RankingRepository


class RankingController:
    """Controlador facade para operações de ranking.

    O controlador delega persistência para uma implementação de RankingRepository.
    Se uma URI Mongo é fornecida e o repositório Mongo está disponível, self._mongo
    conterá a instância MongoRankingRepository; caso contrário self._mongo é
    None e um JsonRankingRepository é usado internamente.
    """

    def __init__(
        self, mongo_uri: Optional[str] = None, data_file: str = "data/rankings.json"
    ):
        # Repositório usado para persistência
        self._repo: RankingRepository
        # Se usar Mongo, expõe via self._mongo para compatibilidade retroativa
        self._mongo: Optional[RankingRepository] = None

        if mongo_uri is not None and MongoRankingRepository is not None:
            try:
                self._repo = MongoRankingRepository(uri=mongo_uri)
                self._mongo = self._repo
                print("Conectado ao MongoDB com sucesso!")
            except Exception as e:
                # Fallback para repositório JSON
                print(f"Aviso: {e}")
                print("Usando armazenamento local (JSON)")
                self._repo = JsonRankingRepository(data_file)
        else:
            self._repo = JsonRankingRepository(data_file)
            print("Usando armazenamento local (JSON)")

    @property
    def mongo(self) -> Optional[RankingRepository]:
        """Expõe repositório MongoDB para compatibilidade retroativa com código existente."""
        return self._mongo

    # ---- Gerenciamento de usuários ----
    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        return self._repo.create_user(username, password)

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        return self._repo.authenticate_user(username, password)

    # ---- API de Ranking usada pelas views ----
    def add_match_result(
        self,
        player_name: str,
        won: bool,
        turns: int,
        ships_remaining: int,
        accuracy: float,
    ) -> bool:
        """Calcula pontuação e persiste o resultado da partida via repositório."""
        score = self._calculate_score(won, turns, ships_remaining, accuracy)
        return self._repo.add_score(
            player_name, won, turns, ships_remaining, accuracy, score
        )

    def get_top_rankings(self, limit: int = 10) -> List[Dict]:
        return self._repo.get_top_scores(limit)

    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        return self._repo.get_user_stats(player_name)

    def clear_rankings(self) -> bool:
        return self._repo.clear_all()

    def _calculate_score(
        self, won: bool, turns: int, ships_remaining: int, accuracy: float
    ) -> int:
        score = 0
        if won:
            score += 1000
            score += max(0, 500 - (turns * 5))
        # Bônus por navios próprios sobreviventes (0-5 navios × 100 = 0-500 pontos)
        score += ships_remaining * 100
        score += int(accuracy * 500)
        return max(0, score)
