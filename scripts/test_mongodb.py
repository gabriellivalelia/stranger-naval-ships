#!/usr/bin/env python3
"""
Script de teste para verificar a conexão com MongoDB
Execute: python scripts/test_mongodb.py
"""

import os
import sys

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from controller.mongo_controller import MongoController


def test_mongodb():
    """Testa a conexão e operações básicas com MongoDB"""

    print("🔍 Testando conexão com MongoDB...\n")

    # Obter URI do ambiente ou usar padrão
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    print(f"URI: {mongo_uri}")

    try:
        # Tentar conectar
        print("\n1. Conectando ao MongoDB...")
        mongo = MongoController(uri=mongo_uri)
        print("   ✅ Conexão bem-sucedida!\n")

        # Testar criação de usuário
        print("2. Testando criação de usuário...")
        test_user = "test_user"
        test_pass = "test_password_123"

        success = mongo.create_user(test_user, test_pass)
        if success:
            print(f"   ✅ Usuário '{test_user}' criado com sucesso!")
        else:
            print(f"   ⚠️  Usuário '{test_user}' já existe (OK)")

        # Testar autenticação
        print("\n3. Testando autenticação...")
        if mongo.authenticate_user(test_user, test_pass):
            print("   ✅ Autenticação bem-sucedida!")
        else:
            print("   ❌ Falha na autenticação")
            return False

        # Testar autenticação com senha errada
        print("\n4. Testando autenticação com senha errada...")
        if not mongo.authenticate_user(test_user, "senha_errada"):
            print("   ✅ Senha incorreta rejeitada corretamente!")
        else:
            print("   ❌ Erro: senha errada foi aceita!")
            return False

        # Testar adição de score
        print("\n5. Testando adição de score...")
        mongo.add_score(
            username=test_user, won=True, turns=25, ships_destroyed=5, accuracy=0.75
        )
        print("   ✅ Score adicionado!")

        # Testar busca de top scores
        print("\n6. Testando busca de top scores...")
        top_scores = mongo.get_top_scores(limit=5)
        print(f"   ✅ {len(top_scores)} scores encontrados")
        if top_scores:
            print("\n   Top 3:")
            for i, score in enumerate(top_scores[:3], 1):
                print(f"      {i}. {score['player_name']}: {score['score']} pontos")

        # Testar estatísticas do usuário
        print("\n7. Testando estatísticas do usuário...")
        stats = mongo.get_user_stats(test_user)
        if stats:
            print(f"   ✅ Estatísticas de '{test_user}':")
            print(f"      - Partidas: {stats['total_matches']}")
            print(f"      - Vitórias: {stats['wins']}")
            print(f"      - Taxa de vitória: {stats['win_rate']}%")
            print(f"      - Melhor score: {stats['best_score']}")

        print("\n" + "=" * 50)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 50)
        print("\n💡 MongoDB está configurado corretamente!")
        print("   Você pode usar o sistema de ranking online.\n")

        return True

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 Possíveis soluções:")
        print("   1. Verifique se o MongoDB está rodando:")
        print("      $ sudo systemctl status mongodb")
        print("      ou")
        print("      $ docker ps  (se usando Docker)")
        print("\n   2. Verifique a variável MONGO_URI:")
        print(f"      Atual: {mongo_uri}")
        print("\n   3. Instale o MongoDB:")
        print("      $ sudo apt-get install mongodb")
        print("      ou")
        print("      $ docker run -d -p 27017:27017 mongo")
        print(
            "\n   4. O jogo funcionará no modo offline (JSON) se MongoDB não estiver disponível."
        )
        return False


if __name__ == "__main__":
    success = test_mongodb()
    sys.exit(0 if success else 1)
