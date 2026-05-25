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

### Banco (PostgreSQL)

Rodar o `commands.sql` no pgAdmin, copiar `.env.example` para `.env` com a senha, depois:

```bash
py -m pip install psycopg2-binary python-dotenv
py -m banco.seed
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
├── exemplos/                 # Vídeos de exemplo
├── relatorios/               # Relatórios JSON gerados
└── frontend/                 # React
```
