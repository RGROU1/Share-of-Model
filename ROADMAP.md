# Tarefas abertas

Ordenadas por valor didático, não por dificuldade.
Cada uma preenche uma lacuna entre o que o artigo afirma e o que o código demonstra.

## 1. Gráfico de convergência em SVG
**Por quê:** a tabela de convergência é o argumento mais forte do repositório e hoje é só texto. Um SVG sem dependência externa (string formatada à mão, como em `relatorio.py`) tornaria compartilhável.
**Onde:** novo `som/grafico.py`. Sem matplotlib.

## 2. Efeito de desenho amostral
**Por quê:** o artigo declara que execuções do mesmo prompt são mais correlacionadas que execuções de prompts diferentes, e que por isso 900 é piso e não alvo. O código diz isso em comentário mas não calcula.
**O que fazer:** estimar a correlação intraclasse entre execuções do mesmo prompt e derivar o n efetivo.

## 3. Série temporal com quebra de congelamento
**Por quê:** `verificar_congelamento()` existe mas nunca é exercitado no demo.
**O que fazer:** um exemplo que roda duas medições, edita um prompt entre elas e mostra o erro sendo levantado.

## 4. Sentimento como terceira dimensão
**Por quê:** o artigo distingue aparecer, ser recomendado e ser recomendado com ressalva. A regra ponderada cobre as duas primeiras, não a terceira.
**Cuidado:** exigiria classificador, o que quebra a regra de dependência única.

## 5. Comparação entre regras de contagem no mesmo relatório
**Por quê:** `python -m som regras` já roda as três. Uma tabela ainda mais proeminente no relatório principal ajudaria.

## 6. Notebook comentado
**Por quê:** parte do público lê notebook e não lê módulo Python.
**Onde:** `notebooks/01_passo_a_passo.ipynb`.
