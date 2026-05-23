# VetVision — Frontend

Interface web do sistema de monitoramento de pets internados, construída com React 19 + Vite.

## Como rodar

```bash
npm install
npm run dev
```

Acesse em `http://localhost:5173`.

> Certifique-se de que a API Flask está rodando em `http://localhost:5000` antes de usar as funcionalidades de análise de vídeo.

## Scripts disponíveis

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Sobe o servidor de desenvolvimento |
| `npm run build` | Gera o build de produção |
| `npm run preview` | Pré-visualiza o build de produção |
| `npm run lint` | Roda o ESLint |

## Páginas

| Rota | Página |
|------|--------|
| `/` | Login |
| `/painel` | Painel com grade de baias |
| `/baia/:numero` | Detalhes do animal e histórico de alimentação |
| `/cadastro` | Cadastro de novo animal |
