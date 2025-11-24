"""MongoRankingRepository - Implementação de persistência em MongoDB"""

import binascii
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from model.repositories.ranking_repository import RankingRepository

try:
    from pymongo import MongoClient, errors
except ImportError:
    MongoClient = None


def _hash_password(password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
    """Gera hash de senha com salt"""
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return {
        "salt": binascii.hexlify(salt).decode("ascii"),
        "hash": binascii.hexlify(dk).decode("ascii"),
    }


class MongoRankingRepository(RankingRepository):
    """Implementação de repositório usando MongoDB"""

    def __init__(self, uri: Optional[str] = None, db_name: str = "stranger_ships"):
        """
        Inicializa o repositório MongoDB.

        Args:
            uri: URI de conexão do MongoDB
            db_name: Nome do banco de dados

        Raises:
            RuntimeError: Se não conseguir conectar ao MongoDB
        """
        if MongoClient is None:
            raise RuntimeError(
                "pymongo is not installed. Install with `pip install pymongo`."
            )

        self._uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self._db_name = db_name
        self._client = None
        self._db = None
        self._connect()

    def _connect(self) -> None:
        """Conecta ao MongoDB"""
        try:
            self._client = MongoClient(
                self._uri,
                serverSelectionTimeoutMS=1000,  # 1 second timeout
                connectTimeoutMS=1000,
                socketTimeoutMS=1000,
            )
            # Trigger server selection
            self._client.admin.command("ping")
            self._db = self._client[self._db_name]
            self._ensure_indexes()
        except Exception:
            raise RuntimeError(
                "MongoDB não disponível. O jogo usará armazenamento local (JSON)."
            )

    def _ensure_indexes(self) -> None:
        """Cria índices necessários"""
        # users collection: unique username
        users = self._db.get_collection("users")
        users.create_index("username", unique=True)
        # scores collection: index by score desc
        scores = self._db.get_collection("scores")
        scores.create_index("score")

    def create_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Cria um novo usuário"""
        users = self._db.get_collection("users")
        creds = _hash_password(password)
        doc = {
            "username": username,
            "password_hash": creds["hash"],
            "salt": creds["salt"],
            "created_at": datetime.utcnow(),
        }
        try:
            users.insert_one(doc)
            return (True, "Usuário criado com sucesso")
        except errors.DuplicateKeyError:
            return (False, "Usuário já existe")

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Autentica um usuário"""
        users = self._db.get_collection("users")
        doc = users.find_one({"username": username})
        if not doc:
            return (False, "Usuário não encontrado")

        salt = binascii.unhexlify(doc["salt"].encode("ascii"))
        candidate = _hash_password(password, salt)["hash"]

        if candidate == doc["password_hash"]:
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
        scores = self._db.get_collection("scores")
        doc = {
            "username": username,
            "won": bool(won),
            "turns": int(turns),
            "ships_remaining": int(ships_remaining),
            "accuracy": float(accuracy),
            "score": int(score),
            "date": datetime.utcnow(),
        }
        scores.insert_one(doc)
        return True

    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """Retorna os melhores resultados"""
        scores = self._db.get_collection("scores")
        docs = scores.find().sort("score", -1).limit(limit)
        return [self._serialize_score(d) for d in docs]

    def get_user_stats(self, username: str) -> Optional[Dict]:
        """Retorna estatísticas de um jogador"""
        scores = self._db.get_collection("scores")
        docs = list(scores.find({"username": username}))
        if not docs:
            return None

        total_matches = len(docs)
        wins = sum(1 for d in docs if d.get("won"))
        total_score = sum(d.get("score", 0) for d in docs)
        avg_accuracy = sum(d.get("accuracy", 0) for d in docs) / total_matches
        best_score = max(d.get("score", 0) for d in docs)

        return {
            "player_name": username,
            "total_matches": total_matches,
            "wins": wins,
            "losses": total_matches - wins,
            "win_rate": round((wins / total_matches) * 100, 2),
            "total_score": total_score,
            "average_accuracy": round(avg_accuracy * 100, 2),  # Convert to percentage
            "best_score": best_score,
        }

    def clear_all(self) -> bool:
        """Limpa todos os rankings"""
        try:
            self._db.get_collection("scores").delete_many({})
            return True
        except Exception:
            return False

    def _serialize_score(self, doc: Dict) -> Dict:
        """Serializa documento do MongoDB para formato padrão"""
        return {
            "player_name": doc.get("username"),
            "won": bool(doc.get("won")),
            "turns": int(doc.get("turns", 0)),
            "ships_remaining": int(doc.get("ships_remaining", 0)),
            "accuracy": round(
                float(doc.get("accuracy", 0.0)) * 100, 2
            ),  # To percentage
            "score": int(doc.get("score", 0)),
            "date": doc.get("date"),
        }
