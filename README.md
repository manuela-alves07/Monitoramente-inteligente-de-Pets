# VetVision — Monitoramento Inteligente de Pets

Sistema de monitoramento de animais internados em clínicas veterinárias com detecção de comportamento via IA.

---

## Tecnologias

- **Frontend:** React 19 + Vite
- **Backend:** Flask (Python)
- **Banco de dados:** PostgreSQL (Neon)
- **IA:** Roboflow (modelo treinado com YOLOv8) + OpenCV + tracker de centroide

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
| `POST` | `/baias` | Cria uma nova baia |
| `DELETE` | `/baias/<id>` | Remove uma baia (somente se vazia) |
| `GET` | `/animais` | Lista todos os animais |
| `POST` | `/animais` | Cadastra um novo animal |
| `PUT` | `/animais/<id>` | Atualiza dados do animal |
| `POST` | `/animais/<id>/baixa` | Dá alta ao animal |
| `POST` | `/animais/<id>/transferir` | Transfere animal para outra baia |
| `PUT` | `/animais/<id>/observacoes` | Salva observações clínicas |
| `GET` | `/animais/<id>/eventos` | Lista eventos de um animal |
| `GET` | `/usuarios` | Lista usuários cadastrados |
| `POST` | `/usuarios` | Cadastra um novo usuário |
| `POST` | `/usuarios/login` | Autentica um usuário |
| `PUT` | `/usuarios/<id>/senha` | Atualiza senha (admin) |
| `PUT` | `/usuarios/me/senha` | Troca a própria senha |
| `DELETE` | `/usuarios/<id>` | Remove um usuário |
| `GET` | `/alertas` | Lista alertas clínicos abertos com nome do animal |
| `POST` | `/alertas/<id>/fechar` | Marca um alerta como resolvido |
| `GET` | `/animais/<id>/alertas` | Lista todos os alertas de um animal (histórico) |
| `POST` | `/analisar` | Recebe vídeo, analisa comportamento e salva eventos |
| `GET` | `/relatorios` | Lista relatórios gerados |
| `GET` | `/relatorios/<nome>` | Retorna relatório em JSON |

---

## Estrutura

```
├── app.py                    # API Flask
├── analisar_comportamento.py # Detecção via Roboflow + tracker + lógica de comportamento
├── requirements.txt
├── .env                      # Credenciais do banco (não commitado)
├── banco/
│   ├── database.py           # Conexão com PostgreSQL
│   └── repositorio.py        # Funções de acesso ao banco
├── exemplos/                 # Vídeos de exemplo
├── relatorios/               # Relatórios JSON gerados
├── uploads/                  # Vídeos enviados pelo sistema
└── frontend/                 # React + Vite
```

---

## Usuário padrão

| Login | Senha | Perfil |
|-------|-------|--------|
| admin | admin123 | Administrador |
