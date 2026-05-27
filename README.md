# VetVision — Monitoramento Inteligente de Pets

Sistema de monitoramento de animais internados em clínicas veterinárias com detecção de comportamento alimentar via IA (YOLOv8).

---

## Tecnologias

- **Frontend:** React 19 + Vite
- **Backend:** Flask (Python)
- **Banco de dados:** PostgreSQL (Neon)
- **IA:** YOLOv8 (Ultralytics) + OpenCV

---

## Configuração

Crie o arquivo `.env` na raiz do projeto com as credenciais do banco:

```env
PG_HOST=seu_host_neon
PG_PORT=5432
PG_DB=neondb
PG_USER=neondb_owner
PG_PASSWORD=sua_senha
PG_SSLMODE=require
```

---

## Como rodar

### Backend

```bash
pip install -r requirements.txt
python app.py
```

API disponível em `http://localhost:5000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Painel disponível em `http://localhost:5173`

> O backend precisa estar rodando para o painel e a análise de vídeo funcionarem.

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/baias` | Lista todas as baias com animais internados |
| `GET` | `/animais` | Lista todos os animais |
| `POST` | `/animais` | Cadastra um novo animal em uma baia |
| `POST` | `/animais/<id>/baixa` | Dá alta a um animal e libera a baia |
| `GET` | `/animais/<id>/eventos` | Lista eventos de um animal |
| `GET` | `/usuarios` | Lista usuários cadastrados |
| `POST` | `/usuarios` | Cadastra um novo usuário |
| `POST` | `/usuarios/login` | Autentica um usuário |
| `PUT` | `/usuarios/<id>/senha` | Atualiza a senha de um usuário |
| `DELETE` | `/usuarios/<id>` | Remove um usuário |
| `POST` | `/analisar` | Recebe um vídeo e retorna relatório de alimentação |
| `GET` | `/relatorios` | Lista os relatórios gerados |
| `GET` | `/relatorios/<nome>` | Retorna um relatório em JSON |
| `GET` | `/video/<nome>` | Retorna um vídeo analisado |

---

## Estrutura

```
├── app.py                    # API Flask
├── detectar_objetos.py       # Detecção com YOLOv8
├── analisar_comportamento.py # Análise de comportamento alimentar
├── alertas.py                # Geração de alertas
├── requirements.txt
├── .env                      # Credenciais do banco (não commitado)
├── banco/
│   ├── database.py           # Conexão com PostgreSQL
│   └── repositorio.py        # Funções de acesso ao banco
├── exemplos/                 # Vídeos de exemplo
├── relatorios/               # Relatórios JSON gerados
└── frontend/                 # React + Vite
```
