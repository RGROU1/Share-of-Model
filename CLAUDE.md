# Contexto do projeto

Leia este arquivo antes de qualquer alteração.

## O que é

Implementação de referência para medir **Share of Model**: o percentual de respostas
geradas por IA em que uma marca é citada, em relação ao total de menções da categoria.

Acompanha o terceiro artigo de uma trilogia publicada no Medium. **O repositório não é
um produto.** É a prova executável de que o método descrito no artigo funciona.

## A restrição que governa todas as decisões

> Cada linha de código precisa ser rastreável até um trecho do artigo.

Se uma funcionalidade não corresponde a nada que o artigo afirma, ela não entra.
Se um trecho do artigo não tem código correspondente, isso é uma lacuna a preencher.

Consequências práticas:

- **Zero setup.** `python -m som demo` roda sem chave de API, sem custo, em segundos.
  Qualquer mudança que quebre isso está errada.
- **Dependência única.** Só `pyyaml`. Não adicione pandas, numpy, scipy ou plotly.
  A estatística é simples o bastante para ser escrita à mão, e ver a fórmula no
  código é parte do valor didático.
- **Docstrings em português**, abrindo com a citação do artigo que justifica o módulo.
- **Comentários explicam o porquê, não o quê.** Quem lê o repositório está aprendendo
  o método, não revisando sintaxe.

## Estrutura

```
som/
  etapa1_escopo.py       Categoria, concorrentes, resolução de entidades
  etapa2_prompts.py      Conjunto de prompts + hash de congelamento
  etapa3_modelos.py      Simulador + esqueleto de adaptadores reais
  etapa4_execucao.py     Rodadas com log de data e versão
  etapa5_codificacao.py  Regras de contagem + normalização de verbosidade
  etapa6_calculo.py      SoM, intervalo de Wilson, variância, convergência
  amostragem.py          n = z²·p(1−p)/E²
  pipeline.py            Orquestra as seis etapas em uma tela
  relatorio.py           Saída em texto, sem dependência externa
config/                  Escopo da categoria (YAML)
prompts/                 Conjuntos congelados (YAML)
tests/                   Verificam que os números batem com o artigo
```

A numeração dos módulos espelha as seis etapas do protocolo. Não renomeie.

## Comandos

```bash
python -m som demo          # pipeline completo
python -m som demo 5        # forçando 5 execuções por combinação
python -m som regras        # compara as três regras de contagem
python -m pytest -q         # testes
```

## Números que não podem mudar sem revisar o artigo

| Valor | Onde | Origem |
|---|---|---|
| 897 | `tamanho_amostra()` | p=0,30, margem=0,03, confiança=95% |
| 2 execuções por combinação | `distribuir(120, 4)` | 897 ÷ 480 arredondado para cima |

Os testes travam esses dois. Se algum quebrar, ou o código regrediu ou o artigo precisa
ser corrigido junto. Nunca ajuste o teste para o código passar.

## Decisões já tomadas, com o motivo

**Intervalo de Wilson e não aproximação normal.** A normal se comporta mal quando a
proporção é próxima de zero, que é o caso de marcas challenger. Trocar seria regressão.

**A verdade do simulador é calculada por Monte Carlo, não pela força latente
normalizada.** O simulador ordena as marcas por força e corta nas N primeiras, então a
participação resultante não é proporcional à força. Usar a força normalizada como
"verdade" foi um bug corrigido.

**A variância é medida por rodada completa, não por prompt individual.** No nível do
prompt, uma resposta ou cita a marca ou não, e o resultado vira 0% ou 100%. Share of
Model só existe sobre um conjunto.

**Os adaptadores de API estão incompletos de propósito.** Manter integração com três
provedores desatualiza rápido, e integração quebrada engana mais do que ajuda.

## O que não fazer

- Não transforme em ferramenta de produção. Já existem, algumas open source.
  O diferencial deste repositório é ser pequeno e legível.
- Não adicione dashboard, banco de dados ou API web.
- Não use dados reais de marcas reais nos exemplos. As marcas do demo são fictícias
  de propósito.
- Não remova as ressalvas metodológicas dos docstrings. Elas são o conteúdo.

## Tarefas abertas

Em `ROADMAP.md`.
