"""JsonRankingRepository - Implementação de persistência em arquivo JSON"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from model.repositories.ranking_repository import RankingRepository


class JsonRankingRepository(RankingRepository):
    """Implementação de repositório usando arquivo JSON local"""

    def __init__(self, data_file: str = "data/rankings.json"):
        """
        Inicializa o repositório JSON.

        Args:
            data_file: Caminho para o arquivo JSON
        """
        self._data_file = Path(data_file)
        self._users_file = Path(data_file).parent / "users.json"
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Garante que os arquivos de dados existem"""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self._data_file.exists():
            self._save_json(self._data_file, [])

        if not self._users_file.exists():
            self._save_json(self._users_file, {})

    def _save_json(self, file_path: Path, data):
        """Salva dados em arquivo JSON"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar {file_path}: {e}")

    def _load_json(self, file_path: Path):
        """Carrega dados de arquivo JSON"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar {file_path}: {e}")
            return [] if file_path == self._data_file else {}

    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """
        Gera hash de senha com salt.

        Args:
            password: Senha em texto plano
            salt: Salt (gerado se None)

        Returns:
            Tupla (hash, salt)
        """
        if salt is None:
            import os

            salt = os.urandom(32).hex()

        hash_obj = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return hash_obj.hex(), salt

    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Cria um novo usuário"""
        users = self._load_json(self._users_file)

        if username in users:
            return (False, "Usuário já existe")

        password_hash, salt = self._hash_password(password)
        users[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
        }

        self._save_json(self._users_file, users)
        return (True, "Usuário criado com sucesso")

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Autentica um usuário"""
        users = self._load_json(self._users_file)

        if username not in users:
            return (False, "Usuário não encontrado")

        user_data = users[username]
        password_hash, _ = self._hash_password(password, user_data["salt"])

        if password_hash == user_data["password_hash"]:
            return (True, "Login realizado com sucesso")
        else:
            return (False, "Senha incorreta")

    def add_score(
        self,
        username: str,
        won: bool,
        turns: int,
        ships_remaining: int,
        accuracy: float,
        score: int,
    ) -> bool:
        """Adiciona um resultado ao ranking"""
        rankings = self._load_json(self._data_file)

        result = {
            "player_name": username,
            "won": won,
            "turns": turns,
            "ships_remaining": ships_remaining,
            "accuracy": round(accuracy * 100, 2),  # Converte para percentual
            "score": score,
            "date": datetime.now().isoformat(),
        }

        rankings.append(result)
        self._save_json(self._data_file, rankings)
        return True

    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """Retorna os melhores resultados"""
        rankings = self._load_json(self._data_file)
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return rankings[:limit]

    def get_user_stats(self, username: str) -> Optional[Dict]:
        """Retorna estatísticas de um jogador"""
        rankings = self._load_json(self._data_file)
        player_matches = [r for r in rankings if r["player_name"] == username]

        if not player_matches:
            return None

        total_matches = len(player_matches)
        wins = sum(1 for m in player_matches if m["won"])
        total_score = sum(m["score"] for m in player_matches)
        avg_accuracy = sum(m["accuracy"] for m in player_matches) / total_matches
        best_score = max(m["score"] for m in player_matches)

        return {
            "player_name": username,
            "total_matches": total_matches,
            "wins": wins,
            "losses": total_matches - wins,
            "win_rate": round((wins / total_matches) * 100, 2),
            "total_score": total_score,
            "average_accuracy": round(avg_accuracy, 2),
            "best_score": best_score,
        }

    def clear_all(self) -> bool:
        """Limpa todos os rankings"""
        self._save_json(self._data_file, [])
        return True
