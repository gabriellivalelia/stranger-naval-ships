"""Repositories - Camada de persistência de dados"""

from model.repositories.json_ranking_repository import JsonRankingRepository
from model.repositories.ranking_repository import RankingRepository

try:
    from model.repositories.mongo_ranking_repository import MongoRankingRepository
except ImportError:
    MongoRankingRepository = None

__all__ = ["RankingRepository", "JsonRankingRepository", "MongoRankingRepository"]
