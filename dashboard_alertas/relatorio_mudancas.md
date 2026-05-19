# Relatório de Mudanças - Dashboard e Alertas

## Objetivo

Adicionar a parte do dashboard do cliente e o serviço de alertas sem mudar a estrutura principal do projeto.

## O que foi criado

### `dashboard_alertas/dashboard.py`

Dashboard visual para o cliente acompanhar:

- status geral do pet;
- última alimentação;
- quantidade de refeições;
- quantidade de alertas;
- vídeo do monitoramento;
- resumo do período;
- histórico de eventos.

### `dashboard_alertas/servico_alertas.py`

Arquivo responsável por gerar os alertas exibidos no dashboard.

Alertas principais:

- nenhuma refeição detectada;
- muitas aproximações sem alimentação;
- muito tempo sem alimentação.

## O que foi alterado no `detectar_alimentacao.py`

O código foi mantido o mais parecido possível com o original do GitHub.

Mudanças necessárias:

- adicionado import do serviço de alertas;
- relatórios agora são salvos em `dashboard_alertas/relatorios/`;
- alertas são gerados pelo `servico_alertas.py`;
- ao rodar `py detectar_alimentacao.py`, todos os vídeos da pasta `exemplos/` são processados;
- cada relatório recebe o nome do vídeo para não sobrescrever arquivos anteriores.

## Por que essas mudanças foram feitas

Para separar melhor as responsabilidades:

- `detectar_alimentacao.py`: faz a detecção e gera o relatório;
- `servico_alertas.py`: aplica as regras de alerta;
- `dashboard.py`: exibe as informações para o cliente.

Assim a parte do dashboard e alertas fica organizada, mas sem alterar demais o código principal do projeto.
