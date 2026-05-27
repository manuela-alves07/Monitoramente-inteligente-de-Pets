# VetVision — Monitoramento Inteligente de Pets

Sistema de monitoramento de animais internados em clínicas veterinárias com detecção de comportamento alimentar via IA (YOLOv8).

---

## Tecnologias

- **Frontend:** React 19 + Vite
- **Backend:** Flask (Python)
- **IA:** YOLOv8 (Ultralytics) + OpenCV

---

## Como rodar

### Backend

```bash
pip install -r requirements.txt
python app.py
```

API disponível em `http://localhost:5000`

### Banco de dados (PostgreSQL — Neon ou local)

1. Copie `.env.example` → `.env`
2. Cole sua `DATABASE_URL` do Neon (peça ao responsável pelo banco) **entre aspas**:

```env
DATABASE_URL="postgresql://usuario:senha@host.neon.tech/neondb?sslmode=require"
```

3. Teste a conexão:

```powershell
py -c "from banco.database import testar_conexao; print(testar_conexao())"
```

> **Banco novo (1ª vez):** abra `banco/schema.sql` e `banco/migracoes.sql` no **SQL Editor do Neon** (ou pgAdmin) e execute o conteúdo. Depois rode `py -m banco.seed` para popular com a clínica padrão.

Cada clínica tem suas próprias baias; o usuário só vê dados da clínica dele (`id_clinica` no login).

**Criar usuário** (PowerShell, pede ao responsável pelo banco):

```powershell
py -c "from banco.repositorio import inserir_usuario; print(inserir_usuario('Nome', 'email@clinica.com', 'senha123', 1, 'admin'))"
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Painel disponível em `http://localhost:5173`

> O backend precisa estar rodando para a análise de vídeo funcionar.

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/relatorios` | Lista os relatórios gerados |
| `GET` | `/relatorios/<nome>` | Retorna um relatório em JSON |
| `POST` | `/analisar` | Recebe um vídeo e retorna o relatório de alimentação |

---

## Estrutura

```
├── app.py                    # API Flask
├── detectar_objetos.py       # Detecção com YOLOv8
├── analisar_comportamento.py # Análise de alimentação
├── alertas.py                # Geração de alertas
├── requirements.txt
├── banco/                    # PostgreSQL (schema, API de dados)
├── relatorios/               # Relatórios JSON gerados (gitignore)
└── frontend/                 # React
```
