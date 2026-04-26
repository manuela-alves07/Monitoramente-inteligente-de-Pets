# 🐾 Regras de Interpretação de Comportamento

## 📌 Objetivo

Este documento define as regras utilizadas para transformar detecções visuais em **comportamentos interpretáveis**, como alimentação, hidratação, atividade e descanso.

O sistema utiliza detecção de objetos (YOLO) combinada com regras baseadas em **tempo, proximidade e consistência**, evitando decisões baseadas em frames isolados.


## 🧠 Princípio Geral

Nenhum comportamento é definido a partir de um único frame.

Toda inferência considera:

* Proximidade espacial
* Duração temporal
* Estabilidade do comportamento

## 🔍 Detecções Base

O modelo de visão computacional identifica:

* Pet (cachorro/gato)
* Tigela de ração
* Tigela de água

## 🍽️ Regra: Alimentação

Um pet é considerado **comendo** quando:

* Está próximo da tigela de ração
* Mantém posição estável próximo ao objeto
* Permanece nessa condição por um tempo mínimo

### ✔️ Condições

* Distância pet ↔ tigela < threshold
* Duração mínima: 5 segundos
* Baixa variação de posição (não está apenas passando)

### ❗ Regras adicionais

* Interações menores que 2 segundos são ignoradas
* Caso o pet se afaste, o evento é encerrado

## 💧 Regra: Hidratação

Um pet é considerado **bebendo** quando:

* Está próximo da tigela de água
* Permanece por um curto período contínuo

### ✔️ Condições

* Distância pet ↔ tigela < threshold
* Duração mínima: 3 segundos

### ❗ Observações

* Eventos de hidratação são mais curtos que alimentação
* Pequenas pausas são toleradas

## 🧍 Regra: Inatividade

Um pet é considerado **inativo** quando:

* Não apresenta movimentação significativa por um período prolongado

### ✔️ Condições

* Deslocamento mínimo entre frames
* Tempo contínuo sem movimento: 10 minutos


## 🚶 Regra: Atividade

Um pet é considerado **ativo** quando:

* Apresenta deslocamento acima de um limite definido

## 😴 Regra: Descanso / Sono

Um pet é considerado em estado de **descanso** quando:

* Está em posição deitado
* Não apresenta movimentação significativa
* Permanece nessa condição por pelo menos 5 minutos

### ⚖️ Interpretação

* O estado de descanso é considerado normal no ambiente clínico
* Animais podem permanecer em repouso por longos períodos (inclusive várias horas)

### 🚨 Geração de alerta

O descanso isolado não gera alerta.

Alertas são gerados apenas quando o descanso prolongado está associado a outros fatores, como:

* Ausência de alimentação por mais de 6 horas
* Ausência de hidratação por mais de 4 horas
* Baixo nível geral de atividade ao longo do período

### 🔴 Regra de atenção

* Descanso contínuo superior a 3 horas deve ser analisado em conjunto com outros comportamentos
* Caso combinado com ausência de ingestão, pode indicar risco

## ⏱️ Sessões de Comportamento

Eventos contínuos são agrupados em sessões:

* Alimentação
* Hidratação
* Descanso

Cada sessão possui:

* Início
* Fim
* Duração total

## 🚨 Regras Clínicas

As regras clínicas avaliam ausência ou combinação de comportamentos ao longo do tempo.

### Exemplos

* Sem alimentação por 6 horas → alerta
* Sem hidratação por 4 horas → alerta
* Inatividade por mais de 30 minutos → alerta
* Descanso prolongado + ausência de ingestão → alerta

## ⚖️ Validação de Interação

Para confirmar um comportamento, o sistema exige:

* Proximidade (pet + objeto)
* Tempo mínimo
* Consistência

### Fórmula conceitual

Interação = proximidade + tempo + estabilidade


## 🐶🐶 Cenários com Múltiplos Animais

Para ambientes com mais de um pet:

* Cada animal é identificado por tracking (ID)
* Eventos são associados ao ID correspondente

### ❗ Tratamento de conflito

* Se dois animais estiverem muito próximos:

  * O evento pode ser marcado como **incerto**
* Eventos com baixa confiança podem ser descartados

## 🌗 Tratamento de Incerteza

Devido a fatores como:

* iluminação
* oclusão
* posicionamento da câmera

O sistema utiliza:

* Threshold mínimo de confiança: 0.6
* Classificação de eventos por nível:

  * alta confiança
  * média confiança
  * baixa confiança

## 📊 Sistema de Pontuação (Score)

Cada comportamento pode ser validado por um score:

* Proximidade → peso
* Tempo → peso
* Estabilidade → peso

### Exemplo

* Score ≥ 0.7 → comportamento confirmado

## ⚠️ Limitações Conhecidas

* Proximidade não garante interação real
* Objetos semelhantes podem causar confusão
* Tracking pode falhar em sobreposição de animais
* Diferenças de raça e tamanho impactam detecção
