# Share of Model

**Implementação de referência do protocolo de mensuração descrito no Artigo 3 da trilogia.**

Não é uma ferramenta de mercado. É o menor código completo que executa o método, com cada etapa rastreável até o trecho do artigo que a justifica.

```bash
pip install -e .
python -m som demo
```

Sem chave de API. Sem custo. Roda em segundos.

---

## O que o demo mostra

1. **Share of Model consolidado** de quatro marcas fictícias em quatro modelos simulados.
2. **Comparação medido × verdade** (só possível no modo simulado) — o intervalo de confiança contém o valor verdadeiro?
3. **Tabela de convergência**: com poucas observações a margem de erro é enorme; com ~900 ela cai para a ordem de 2–3 pontos.

```
O PIPELINE ACERTOU? (só possível no modo simulado)
==============================================================================
MARCA          MEDIDO   VERDADE     ERRO   IC CONTÉM?
------------------------------------------------------------------------------
Marca A         55.x%     55.x%    ±0.xp   sim
Marca B         26.x%     26.x%    ±0.xp   sim
...
```

```
CONVERGÊNCIA: quantas execuções bastam?
==============================================================================
     n   SoM MEDIDO     ERRO    MARGEM   DENTRO?
------------------------------------------------------------------------------
    10        xx.x%    ±x.xp     20.xp   sim
   ...
   900        xx.x%    ±0.xp      2.xp   sim
```

Também disponível:

```bash
python -m som regras          # compara PRESENÇA × PRIMEIRA × PONDERADA
python -m pytest -q           # trava os números do artigo
```

---

## A trilogia

| # | Artigo | O que estabelece |
|---|--------|------------------|
| 1 | A métrica que decide quais marcas a IA recomenda | Por que SEO/GEO não bastam; autoridade migrando do domínio para o ecossistema |
| 2 | Como os modelos escolhem quem recomendar | Intenção, funil e o custo de aquisição invisível |
| 3 | **O framework de mensuração em seis etapas** | **Este repositório executa o protocolo deste artigo** |

---

## Mapa código ↔ artigo

| Módulo | Trecho do Artigo 3 |
|--------|--------------------|
| `etapa1_escopo.py` | “Escopo largo demais dilui o indicador…” + resolução de entidades |
| `etapa2_prompts.py` | Prompt set congelado + hash que quebra a série se alguém editar |
| `etapa3_modelos.py` | “A diferença entre modelos costuma ser maior que a variação dentro de cada um” |
| `etapa4_execucao.py` | Livro-razão com data, versão e hash |
| `etapa5_codificacao.py` | Regras de contagem + normalização de verbosidade + concordância |
| `etapa6_calculo.py` | SoM + intervalo de Wilson + convergência + erro vs verdade |
| `amostragem.py` | \( n = z^{2} \cdot p(1-p) / E^{2} \) → ≈897 |

Os números **897** e **2 execuções por combinação** estão travados por testes. Se quebrarem, ou o código regrediu ou o artigo precisa ser revisado junto.

---

## Como usar com dados reais

1. Edite `config/categoria_crm.yaml` com sua categoria e todas as variantes de nome.
2. Escreva o conjunto de prompts em `prompts/`. Depois de escrito, **não edite**. Crie um `v2` se precisar de perguntas novas.
3. Implemente `ModeloAoVivo.responder()` para seus provedores. Registre sempre a versão exata.
4. Rode com a distribuição que `tamanho_amostra()` indicar.

Custo aproximado: 120 prompts × 4 modelos × 2 execuções = 960 chamadas por rodada.

---

## Limitações declaradas

- Extração de menções por resolução de aliases (não NER).
- Sem análise de sentimento.
- Sem detecção de citação de fonte.
- Dados do demo são sintéticos e fictícios de propósito.
- Adaptadores de API estão incompletos de propósito (código de integração quebrado engana mais do que ajuda).

---

## Decisões técnicas

- **Intervalo de Wilson** (não aproximação normal) — a normal se comporta mal perto de 0%.
- **Verdade do simulador por Monte Carlo**, não pela força latente normalizada.
- **Variância por rodada completa**, não por prompt individual.
- **Dependência única: `pyyaml`**. Estatística escrita à mão (valor didático).

Veja `ROADMAP.md` para as lacunas ainda abertas e `CLAUDE.md` para as regras internas do projeto.

---

*O conceito de Share of Model foi proposto por Tom Roach na Marketing Week em 2024. A metodologia deste repositório é uma compilação das fontes citadas no Artigo 3, não um padrão estabelecido.*

Licença: MIT.
