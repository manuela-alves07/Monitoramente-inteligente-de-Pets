# 🐾 Regras de Interpretação de Comportamento

## 📌 Objetivo

Este documento define as regras utilizadas para transformar detecções visuais em **comportamentos interpretáveis**, como alimentação, hidratação, atividade, descanso e interações entre animais.

O sistema utiliza detecção de objetos (YOLO), tracking por ID e regras baseadas em **tempo, proximidade, estabilidade e contexto**, evitando decisões baseadas em frames isolados.

---

## 🧠 Princípio Geral

Nenhum comportamento é definido a partir de um único frame.

Toda inferência considera:

* Proximidade espacial
* Duração temporal
* Estabilidade do comportamento
* Contexto do ambiente
* Histórico recente do animal

---

## 🔍 Detecções Base

O modelo de visão computacional identifica:

* Pet (cachorro/gato)
* Tigela de ração
* Tigela de água

Além disso, o sistema utiliza tracking para manter um ID por animal durante a análise.

---

## 📊 Sistema de Pontuação (Score)

Cada comportamento é validado através de score:

* Proximidade → peso
* Tempo → peso
* Estabilidade → peso
* Contexto → peso

### Exemplo

* Score ≥ 0.7 → comportamento confirmado
* Score entre 0.5 e 0.7 → comportamento incerto
* Score < 0.5 → comportamento descartado


## 🌗 Tratamento de Incerteza

Devido a fatores como:

* iluminação
* oclusão
* posicionamento da câmera
* sobreposição entre animais

O sistema utiliza thresholds de confiança:

* confiança > 0.7 → alta confiança
* entre 0.5 e 0.7 → média confiança
* abaixo de 0.5 → descartar evento


## 🍽️ Alimentação

Um pet é considerado **comendo** quando:

* Está próximo da tigela de ração
* Mantém posição estável
* Permanece nessa condição por tempo suficiente

### ✔️ Regras

* Distância pet ↔ tigela ≤ ~50% da largura do pet
* Tempo mínimo: 5 segundos
* Baixa variação de posição (< ~5% do tamanho do pet)
* Pequenos movimentos repetitivos da cabeça podem reforçar o score
* O pote precisa ser identificado como pote de ração

### ❗ Validação extra

* Interações menores que 2 segundos são classificadas como **cheirando**, não como alimentação
* Caso o pet se afaste rapidamente, o evento é encerrado
* Continuidade próxima ao pote aumenta confiança


## 💧 Hidratação

Um pet é considerado **bebendo** quando:

* Está próximo da tigela de água
* Permanece por curto período contínuo

### ✔️ Regras

* Distância pet ↔ tigela ≤ ~50% da largura do pet
* Tempo mínimo: 3 segundos
* Baixa variação de posição
* Movimento rápido/repetitivo da cabeça pode reforçar a inferência
* Pote identificado como água

### ❗ Observações

* Eventos de hidratação são mais curtos que alimentação
* Pequenas pausas são toleradas
* Frequência de hidratação ao longo do dia pode ser analisada


## 👃 Cheirando

Um pet é considerado **cheirando** quando:

* Está próximo ao pote
* Permanece por pouco tempo
* Não apresenta padrão de alimentação ou hidratação

### ✔️ Regras

* Tempo curto (< 2 segundos)
* Sem movimentos repetitivos
* Entrada e saída rápida do local

## 🧍 Inatividade

Um pet é considerado **inativo** quando:

* Não apresenta movimentação significativa por período prolongado

### ✔️ Regras

* Deslocamento mínimo entre frames (< ~5% do tamanho do pet)
* Tempo contínuo sem movimento: 10 minutos

## 🚶 Atividade

Um pet é considerado **ativo** quando:

* Apresenta deslocamento relevante no ambiente

### ✔️ Regras

* Deslocamento > ~15% do tamanho do pet
* Mudança constante de posição
* Interação frequente com ambiente


## 😴 Descanso / Sono

Um pet é considerado em **descanso** quando:

* Está deitado
* Sem movimentação significativa
* Por pelo menos 5 minutos

### ⚖️ Interpretação

* Descanso é comportamento normal
* Animais podem permanecer em repouso por várias horas

### 🚨 Geração de alerta

O descanso isolado não gera alerta.

Alertas são gerados apenas quando combinado com:

* Ausência de alimentação por mais de 6 horas
* Ausência de hidratação por mais de 4 horas
* Baixo nível geral de atividade

### 🔴 Regra de atenção

* Descanso contínuo > 3 horas deve ser analisado em conjunto com outros fatores

## 😟 Apatia

Um pet pode ser considerado **apático** quando:

* Permanece muito tempo sem atividade
* Não interage com água ou comida
* Demonstra redução significativa de comportamento

### ✔️ Regras

* Inatividade prolongada (> 2 horas)
* Pouca interação com ambiente
* Diferença relevante em relação ao padrão normal do animal


## 😰 Estresse / Agitação

Um pet pode ser considerado **agitado** quando:

* Apresenta movimentação excessiva ou repetitiva

### ✔️ Regras

* Movimento constante no ambiente
* Longo período ativo (> 15 minutos)
* Caminhar repetidamente em padrões semelhantes
* Interação frequente com grades/portas

## 🐶🐶 Interação entre animais

### ✔️ Interação normal

* Aproximação curta
* Movimento leve
* Separação rápida
* Sem sinais agressivos

### ⚠️ Interação problemática

* Proximidade excessiva por tempo prolongado
* Movimentos bruscos/intensos
* Sobreposição significativa entre corpos
* Dificuldade de separação pelo tracking


## 🐶🐶 Cenários com múltiplos animais

Para ambientes com mais de um pet:

* Cada animal é identificado por tracking (ID)
* Eventos são associados ao ID correspondente

### ❗ Tratamento de conflito

* Se dois animais estiverem muito próximos:
  * Evento pode ser marcado como **incerto**
  * Sobreposição > ~30% aumenta nível de incerteza
  * Eventos com baixa confiança podem ser descartados


## 🚨 Regras Clínicas

As regras clínicas avaliam ausência ou combinação de comportamentos ao longo do tempo.

### Exemplos

* Sem alimentação por 6 horas → alerta
* Sem hidratação por 4 horas → alerta
* Inatividade por mais de 30 minutos → alerta
* Descanso prolongado + ausência de ingestão → alerta
* Queda anormal no padrão de atividade → alerta


## ⏱️ Sessões de Comportamento

Eventos contínuos são agrupados em sessões:

* Alimentação
* Hidratação
* Descanso
* Atividade
* Cheirando

Cada sessão possui:

* Início
* Fim
* Duração total


## ⚖️ Validação de Interação

Para confirmar um comportamento, o sistema exige:

* Proximidade
* Tempo mínimo
* Consistência
* Contexto compatível

### Fórmula conceitual

**Interação = proximidade + tempo + estabilidade + contexto**


## ⚠️ Limitações Conhecidas

* Proximidade não garante interação real
* Objetos semelhantes podem causar confusão
* Tracking pode falhar em sobreposição de animais
* Diferenças de raça e tamanho impactam detecção
* Condições de iluminação podem reduzir precisão
* Alguns comportamentos podem ser ambíguos sem contexto clínico adicional
