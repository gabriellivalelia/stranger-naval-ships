import os
from pathlib import Path

from controller.main_controller import MainController

# Carrega variáveis de ambiente do arquivo .env
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key] = value

if __name__ == "__main__":
    play = MainController()
    play.run()
