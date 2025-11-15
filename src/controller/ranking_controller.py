"""RankingController - gerencia salvamento e carregamento de rankings"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Optional MongoDB backend
try:
    from controller.mongo_controller import MongoController
except Exception:
    MongoController = None


class RankingController:
    """Controller responsável por gerenciar o sistema de rankings"""

    def __init__(
        self, data_file: str = "data/rankings.json", mongo_uri: Optional[str] = None
    ):
        """
        Inicializa o controller de rankings.

        Args:
            data_file: Caminho para o arquivo JSON de rankings
        """
        self.data_file = Path(data_file)
        self._ensure_data_file()
        self.mongo = None
        if mongo_uri and MongoController is not None:
            try:
                self.mongo = MongoController(uri=mongo_uri)
            except Exception as e:
                print(f"Warning: could not connect to MongoDB: {e}")

    def _ensure_data_file(self):
        """Garante que o arquivo de dados existe"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_rankings([])

    def _save_rankings(self, rankings: List[Dict]):
        """Salva rankings no arquivo JSON"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(rankings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar rankings: {e}")

    def _load_rankings(self) -> List[Dict]:
        """Carrega rankings do arquivo JSON"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar rankings: {e}")
            return []

    def add_match_result(
        self,
        player_name: str,
        won: bool,
        turns: int,
        ships_destroyed: int,
        accuracy: float,
    ) -> bool:
        """
        Adiciona resultado de uma partida ao ranking.

        Args:
            player_name: Nome do jogador
            won: True se o jogador venceu
            turns: Número de turnos da partida
            ships_destroyed: Número de navios destruídos
            accuracy: Precisão dos ataques (0.0 a 1.0)

        Returns:
            True se salvou com sucesso
        """
        # If Mongo backend available, use it
        if self.mongo:
            return self.mongo.add_score(
                player_name, won, turns, ships_destroyed, accuracy
            )

        rankings = self._load_rankings()

        result = {
            "player_name": player_name,
            "won": won,
            "turns": turns,
            "ships_destroyed": ships_destroyed,
            "accuracy": round(accuracy * 100, 2),  # Convert to percentage
            "score": self._calculate_score(won, turns, ships_destroyed, accuracy),
            "date": datetime.now().isoformat(),
        }

        rankings.append(result)
        self._save_rankings(rankings)
        return True

    def _calculate_score(
        self, won: bool, turns: int, ships_destroyed: int, accuracy: float
    ) -> int:
        """
        Calcula pontuação baseada no desempenho.

        Args:
            won: Vitória
            turns: Número de turnos
            ships_destroyed: Navios destruídos
            accuracy: Precisão (0.0 a 1.0)

        Returns:
            Pontuação calculada
        """
        score = 0

        # Base points for winning
        if won:
            score += 1000

        # Bonus for fewer turns (faster victory)
        if won:
            score += max(0, 500 - (turns * 5))

        # Points for ships destroyed
        score += ships_destroyed * 100

        # Bonus for accuracy
        score += int(accuracy * 500)

        return max(0, score)

    def get_top_rankings(self, limit: int = 10) -> List[Dict]:
        """
        Retorna os melhores rankings ordenados por pontuação.

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de rankings ordenada por score
        """
        if self.mongo:
            return self.mongo.get_top_scores(limit)

        rankings = self._load_rankings()
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return rankings[:limit]

    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """
        Retorna estatísticas de um jogador específico.

        Args:
            player_name: Nome do jogador

        Returns:
            Dicionário com estatísticas ou None se não houver dados
        """
        if self.mongo:
            return self.mongo.get_user_stats(player_name)

        rankings = self._load_rankings()
        player_matches = [r for r in rankings if r["player_name"] == player_name]

        if not player_matches:
            return None

        total_matches = len(player_matches)
        wins = sum(1 for m in player_matches if m["won"])
        total_score = sum(m["score"] for m in player_matches)
        avg_accuracy = sum(m["accuracy"] for m in player_matches) / total_matches
        best_score = max(m["score"] for m in player_matches)

        return {
            "player_name": player_name,
            "total_matches": total_matches,
            "wins": wins,
            "losses": total_matches - wins,
            "win_rate": round((wins / total_matches) * 100, 2),
            "total_score": total_score,
            "average_accuracy": round(avg_accuracy, 2),
            "best_score": best_score,
        }

    def get_all_stats(self) -> Dict:
        """
        Retorna estatísticas gerais do jogo.

        Returns:
            Dicionário com estatísticas globais
        """
        if self.mongo:
            # Construct aggregate from top scores
            top = self.mongo.get_top_scores(1000)
            if not top:
                return {
                    "total_matches": 0,
                    "total_wins": 0,
                    "total_losses": 0,
                    "average_accuracy": 0,
                    "highest_score": 0,
                }
            total_matches = len(top)
            total_wins = sum(1 for r in top if r.get("won"))
            avg_accuracy = sum(r.get("accuracy", 0) for r in top) / total_matches
            highest_score = max(r.get("score", 0) for r in top)
            return {
                "total_matches": total_matches,
                "total_wins": total_wins,
                "total_losses": total_matches - total_wins,
                "average_accuracy": round(avg_accuracy, 2),
                "highest_score": highest_score,
            }

        rankings = self._load_rankings()

        if not rankings:
            return {
                "total_matches": 0,
                "total_wins": 0,
                "total_losses": 0,
                "average_accuracy": 0,
                "highest_score": 0,
            }

        total_matches = len(rankings)
        total_wins = sum(1 for r in rankings if r["won"])
        avg_accuracy = sum(r["accuracy"] for r in rankings) / total_matches
        highest_score = max(r["score"] for r in rankings)

        return {
            "total_matches": total_matches,
            "total_wins": total_wins,
            "total_losses": total_matches - total_wins,
            "average_accuracy": round(avg_accuracy, 2),
            "highest_score": highest_score,
        }

    def clear_rankings(self) -> bool:
        """
        Limpa todos os rankings.

        Returns:
            True se limpou com sucesso
        """
        if self.mongo:
            # Drop all scores collection
            try:
                self.mongo.db.get_collection("scores").delete_many({})
                return True
            except Exception:
                return False

        self._save_rankings([])
        return True
