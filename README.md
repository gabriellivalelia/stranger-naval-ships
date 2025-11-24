# 🚢 Stranger Ships

Jogo de Batalha Naval temático inspirado em Stranger Things - Implementação em Python com arquitetura MVC.

## � Pré-requisitos

### 1. Instalar uv (Gerenciador de Pacotes Python)

**uv** é um gerenciador de pacotes Python extremamente rápido, escrito em Rust.

#### Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell):

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Documentação oficial**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

### 2. Instalar Docker

Necessário para usar o sistema de ranking online com MongoDB.

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS/Linux)
- Ou Docker Engine para Linux: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

## 🚀 Início Rápido

### Passo a Passo Completo

#### 1. Clone o repositório

```bash
git clone https://github.com/gabriellivalelia/stranger-naval-ships
cd stranger-naval-ships
```

#### 2. Instalar dependências

```bash
uv sync
```

#### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

#### 4. Iniciar o banco de dados

**Apenas se quiser usar ranking online:**

```bash
docker compose up -d
```

Isso iniciará:

- MongoDB na porta 27017

#### 5. Iniciar o jogo

```bash
uv run src/main.py
```

## 🎮 Como Jogar

### Fluxo do Jogo

1. **Tela Inicial**: Escolha entre jogar como convidado ou fazer login
2. **Preparação**: Posicione seus 5 navios no tabuleiro
   - Clique para posicionar
   - Pressione `R` ou botão direito do mouse para rotacionar
   - Botão "Randomize" para posicionamento automático
3. **Combate**: Ataque o tabuleiro inimigo
   - Clique em uma célula para atacar
   - 🎯 Acerto / 💧 Água / 💥 Navio destruído
4. **Vitória**: Destrua todos os navios inimigos antes que destruam os seus!

### Controles

- **Mouse**: Clicar para posicionar/atacar
- **R**: Rotacionar navio
- **TAB**: Alternar campos de entrada (login)
- **ENTER**: Confirmar ação
- **ESC**: Voltar/Sair

## 📝 Comandos Disponíveis

```bash
uv run src/main.py          # Inicia o jogo
uv run scripts/test_mongodb.py    # Testa conexão com MongoDB
```

## 🗄️ Banco de Dados

### Requisitos

- MongoDB 7.0+

### Modo de Funcionamento

O jogo possui **dois modos de persistência**:

#### Modo Offline (Padrão)

- Rankings salvos em arquivo JSON local (`data/rankings.json`)
- Não requer configuração adicional
- Funciona sem internet

#### Modo Online (MongoDB)

- Rankings salvos em banco de dados MongoDB
- Suporte a autenticação de usuários com criptografia bcrypt
- Estatísticas persistentes globais
- Fallback automático para modo offline se MongoDB estiver indisponível

## 🎨 Características

### Navios Temáticos

- **Arcade Ship** (5 células) - Inspirado no Palace Arcade
- **Argyle's Van Ship** (4 células) - A van do Argyle
- **Christmas Ship** (3 células) - Luzes de Natal
- **Demogorgon Ship** (3 células) - O monstro
- **Scoops Ahoy Ship** (2 células) - Sorveteria do Steve

### Sistema de Pontuação

Score calculado com base em:

- **Base**: 1000 pontos por vitória
- **Eficiência**: Até 500 pontos (menos turnos = mais pontos)
- **Sobrevivência**: 100 pontos por navio próprio restante
- **Precisão**: Até 500 pontos (taxa de acerto)

**Score máximo teórico**: 2500 pontos

### Inteligência Artificial

- Modo de **busca aleatória** inteligente
- Modo de **caça adaptativa** após acertar um navio

## 🏗️ Arquitetura

O projeto segue o padrão **MVC (Model-View-Controller)** com aplicação de padrões de projeto:

- **Strategy Pattern**: Jogadores intercambiáveis (humano vs IA)
- **Repository Pattern**: Abstração de persistência (MongoDB vs JSON)
- **Template Method**: Classe base para todas as telas
- **Factory Pattern**: Criação de navios temáticos

## 📚 Documentação

- [Relatório Técnico e diagramas UML](docs/)

## 📖 Links Úteis

- **Documentação do uv**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **Documentação do Pygame**: [https://www.pygame.org/docs/](https://www.pygame.org/docs/)
- **Documentação do PyMongo**: [https://pymongo.readthedocs.io/](https://pymongo.readthedocs.io/)
