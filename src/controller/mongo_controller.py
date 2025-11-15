"""MongoController - lightweight MongoDB integration for users and scores

Provides:
- create_user(username, password)
- authenticate_user(username, password)
- add_score(username, won, turns, ships_destroyed, accuracy)
- get_top_scores(limit)
- get_user_stats(username)

Fallback behavior: if MongoDB is not available, methods raise a RuntimeError.

Configuration:
- MONGO_URI environment variable (default: mongodb://localhost:27017)
- DB name: stranger_ships

Security:
- Passwords are stored using PBKDF2-HMAC-SHA256 with a random salt.
"""

from __future__ import annotations

import binascii
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional

try:
    from pymongo import MongoClient, errors
except Exception:  # pragma: no cover - pymongo may not be installed in the runner
    MongoClient = None  # type: ignore


def _hash_password(password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
    """Return dict with 'salt' and 'hash' hex strings."""
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return {
        "salt": binascii.hexlify(salt).decode("ascii"),
        "hash": binascii.hexlify(dk).decode("ascii"),
    }


class MongoController:
    def __init__(self, uri: Optional[str] = None, db_name: str = "stranger_ships"):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connected = False
        self._connect()

    def _connect(self) -> None:
        if MongoClient is None:
            raise RuntimeError(
                "pymongo is not installed. Install with `pip install pymongo`."
            )
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            # trigger server selection
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self._ensure_indexes()
            self.connected = True
        except Exception as exc:
            self.connected = False
            raise RuntimeError(f"Could not connect to MongoDB at {self.uri}: {exc}")

    def _ensure_indexes(self) -> None:
        # users collection: unique username
        users = self.db.get_collection("users")
        users.create_index("username", unique=True)
        # scores collection: index by score desc
        scores = self.db.get_collection("scores")
        scores.create_index("score")

    # --- User management ---
    def create_user(self, username: str, password: str) -> bool:
        """Create a new user. Returns True if created, False if username exists."""
        if not self.connected:
            raise RuntimeError("MongoDB not connected")
        users = self.db.get_collection("users")
        creds = _hash_password(password)
        doc = {
            "username": username,
            "password_hash": creds["hash"],
            "salt": creds["salt"],
            "created_at": datetime.utcnow(),
        }
        try:
            users.insert_one(doc)
            return True
        except errors.DuplicateKeyError:
            return False

    def authenticate_user(self, username: str, password: str) -> bool:
        """Return True if username/password match."""
        if not self.connected:
            raise RuntimeError("MongoDB not connected")
        users = self.db.get_collection("users")
        doc = users.find_one({"username": username})
        if not doc:
            return False
        salt = binascii.unhexlify(doc["salt"].encode("ascii"))
        candidate = _hash_password(password, salt)["hash"]
        return candidate == doc["password_hash"]

    # --- Scores ---
    def add_score(
        self,
        username: str,
        won: bool,
        turns: int,
        ships_destroyed: int,
        accuracy: float,
    ) -> bool:
        """Add a score entry for a user. Returns True on success."""
        if not self.connected:
            raise RuntimeError("MongoDB not connected")
        scores = self.db.get_collection("scores")
        # Simple scoring formula (can be customized)
        score_value = self._calculate_score(won, turns, ships_destroyed, accuracy)
        doc = {
            "username": username,
            "won": bool(won),
            "turns": int(turns),
            "ships_destroyed": int(ships_destroyed),
            "accuracy": float(accuracy),
            "score": int(score_value),
            "date": datetime.utcnow(),
        }
        scores.insert_one(doc)
        return True

    def _calculate_score(
        self, won: bool, turns: int, ships_destroyed: int, accuracy: float
    ) -> int:
        score = 0
        if won:
            score += 1000
            score += max(0, 500 - (turns * 5))
        score += ships_destroyed * 100
        score += int(accuracy * 500)
        return max(0, score)

    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        if not self.connected:
            raise RuntimeError("MongoDB not connected")
        scores = self.db.get_collection("scores")
        docs = scores.find().sort("score", -1).limit(limit)
        return [self._serialize_score(d) for d in docs]

    def get_user_stats(self, username: str) -> Optional[Dict]:
        if not self.connected:
            raise RuntimeError("MongoDB not connected")
        scores = self.db.get_collection("scores")
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
            "average_accuracy": round(avg_accuracy, 2),
            "best_score": best_score,
        }

    def _serialize_score(self, doc: Dict) -> Dict:
        return {
            "player_name": doc.get("username"),  # Use player_name for consistency
            "won": bool(doc.get("won")),
            "turns": int(doc.get("turns", 0)),
            "ships_destroyed": int(doc.get("ships_destroyed", 0)),
            "accuracy": float(doc.get("accuracy", 0.0)),
            "score": int(doc.get("score", 0)),
            "date": doc.get("date"),
        }
