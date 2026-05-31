# Regras de Interpretação de Comportamento

## Objetivo

Este documento define as regras utilizadas para transformar detecções visuais em comportamentos interpretáveis: alimentação, hidratação, descanso, agitação e apatia.

O sistema utiliza detecção via API Roboflow (modelo treinado com YOLOv8), tracking por centroide e regras baseadas em tempo, proximidade e movimento.

---

## Princípio Geral

Nenhum comportamento é definido a partir de um único frame.

Toda inferência considera:

- Proximidade espacial entre animal e pote
- Duração temporal do comportamento
- Histórico de movimentação do animal
- Contexto (perto de comida ou água)

---

## Detecções Base

O modelo identifica três classes:

- `dog` — cachorro
- `cat` — gato
- `bowl` — tigela (pote)

O tracking é feito por centroide manual: a cada frame, cada detecção é associada ao animal mais próximo do frame anterior (distância máxima de 80px). Se nenhum animal estiver próximo, um novo ID é criado.

---

## Distinção dos Potes

Como o modelo detecta apenas `bowl` (sem diferenciar comida de água), a distinção é feita por posição no frame:

- Pote no **lado esquerdo** → água
- Pote no **lado direito** → comida

O vídeo de monitoramento deve ser configurado com o pote de água à esquerda e o de comida à direita.

---

## Comportamentos Detectados

### Alimentação

Animal próximo ao pote de comida (lado direito) por tempo mínimo de **5 segundos**.

- Distância animal ↔ pote ≤ 1.5× a largura do animal
- Tolerância de pausa: 2 segundos (pequenos afastamentos não encerram o evento)
- Interações menores que 5 segundos são classificadas como **cheirando**

### Hidratação

Animal próximo ao pote de água (lado esquerdo) por tempo mínimo de **3 segundos**.

- Mesma lógica de proximidade e tolerância da alimentação
- Eventos de hidratação tendem a ser mais curtos que alimentação

### Cheirando

Animal se aproxima do pote mas não permanece tempo suficiente para confirmar alimentação ou hidratação (menos de 5 segundos para comida ou menos de 3 segundos para água).

### Descanso

Animal com baixo movimento por pelo menos **5 minutos**.

- Movimento médio < 1.5 px/frame (calculado sobre os últimos 30 frames)
- Não está próximo de nenhum pote
- Descanso isolado não gera alerta — só é considerado problema em conjunto com ausência de ingestão

### Agitação

Animal com movimento intenso por mais de **15 minutos**.

- Movimento médio > 15.0 px/frame

### Apatia

Estado visual exibido quando o animal não come e não bebe há mais de **2 horas** desde o início da análise.

---

## Alertas Clínicos

Gerados ao final da análise com base no histórico do vídeo:

| Condição | Alerta |
|----------|--------|
| Sem comer por mais de 6 horas | `sem_alimentacao` — crítico |
| Sem beber por mais de 4 horas | `sem_hidratacao` — crítico |
| Nenhuma refeição detectada no vídeo | `sem_refeicao_detectada` — aviso |

### Exibição no sistema

- O card da baia fica vermelho quando há alerta aberto
- Clicar no card exibe um modal com a descrição do alerta
- O veterinário pode clicar em **"Ciente"** para marcar como resolvido
- A página **Alertas Clínicos** lista todos os alertas abertos de todos os animais

### Resolução automática

Quando um novo vídeo é analisado e detecta eventos:
- Refeição detectada → fecha automaticamente alertas `sem_alimentacao` abertos do animal
- Hidratação detectada → fecha automaticamente alertas `sem_hidratacao` abertos do animal

### Histórico

Alertas resolvidos ficam registrados no banco com `status = 'fechado'` e aparecem no relatório clínico do animal com o status **"Resolvido"**.

---

## Parâmetros

| Parâmetro | Valor |
|-----------|-------|
| Distância máxima animal ↔ pote | 1.5× largura do animal |
| Tempo mínimo comendo | 5 segundos |
| Tempo mínimo bebendo | 3 segundos |
| Tolerância de pausa | 2 segundos |
| Tempo para descanso | 5 minutos |
| Tempo para agitação | 15 minutos |
| Movimento baixo | < 1.5 px/frame |
| Movimento alto | > 15.0 px/frame |
| Confiança mínima Roboflow | 30% |
| Distância máxima tracker | 80 px |
| Processar a cada N frames | 5 |

---

## Limitações Conhecidas

- Distinção dos potes por posição no frame é temporária — depende do posicionamento do vídeo
- Tracking pode falhar se dois animais se sobrepuserem por muitos frames
- Iluminação ruim ou oclusão reduzem a precisão da detecção
- Comportamentos como "dormindo" não são detectáveis — descanso prolongado é a aproximação mais próxima
- O sistema é projetado para uma câmera por baia (um animal por câmera)
