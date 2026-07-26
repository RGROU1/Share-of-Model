"""
Artigo 3, etapa 6:

"O resultado por modelo, por tipo de intenção e consolidado. Sempre
com a média, a dispersão e o número de observações. Um número solto,
sem esses três acompanhamentos, não sustenta decisão nenhuma."

"Share of Model é uma divisão. No numerador, quantas vezes a sua marca
apareceu nas respostas de IA. No denominador, quantas vezes qualquer
marca da categoria apareceu. Multiplica por cem e você tem a sua
participação."

Decisões documentadas:
- Intervalo de Wilson (não aproximação normal) porque a normal se
  comporta mal quando a proporção é próxima de zero (marcas challenger).
- Variância medida por rodada completa, não por prompt individual.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

from som.etapa4_execucao import Rodada
from som.etapa5_codificacao import RegraContagem, codificar_rodada


@dataclass
class ResultadoMarca:
    marca_id: str
    mencoes: float
    som: float
    ic_inferior: float
    ic_superior: float
    n_observacoes: int


def intervalo_wilson(
    sucessos: float,
    n: float,
    z: float = 1.96,
) -> tuple[float, float]:
    """
    Intervalo de confiança de Wilson para uma proporção.

    Preferido à aproximação normal quando p está perto de 0 ou 1.
    """
    if n <= 0:
        return 0.0, 1.0
    p = sucessos / n
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    margem = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, centro - margem), min(1.0, centro + margem)


def calcular_som(
    pesos: dict[str, float],
    marca_ids: Sequence[str],
    n_observacoes: int,
) -> list[ResultadoMarca]:
    """
    Calcula Share of Model e intervalo de Wilson para cada marca.
    """
    total = sum(pesos.values())
    resultados: list[ResultadoMarca] = []

    for mid in marca_ids:
        mencoes = pesos.get(mid, 0.0)
        if total == 0:
            som = 0.0
            lo, hi = 0.0, 1.0
        else:
            som = mencoes / total
            # aproximamos "sucessos" pelo peso e n pelo total de menções
            # (visão conservadora alinhada ao artigo)
            lo, hi = intervalo_wilson(mencoes, total)
        resultados.append(
            ResultadoMarca(
                marca_id=mid,
                mencoes=mencoes,
                som=som,
                ic_inferior=lo,
                ic_superior=hi,
                n_observacoes=n_observacoes,
            )
        )
    return resultados


def som_de_rodada(
    rodada: Rodada,
    marca_ids: Sequence[str],
    regra: RegraContagem = RegraContagem.PRESENCA,
    normalizar_verbosidade: bool = True,
) -> list[ResultadoMarca]:
    pesos = codificar_rodada(rodada, regra, normalizar_verbosidade)
    return calcular_som(pesos, marca_ids, n_observacoes=rodada.n)


def variancia_por_modelo(
    rodada: Rodada,
    marca_ids: Sequence[str],
    regra: RegraContagem = RegraContagem.PRESENCA,
) -> dict[str, dict[str, float]]:
    """
    Reproduz a lógica do gráfico do artigo: o mesmo conjunto medido
    várias vezes (aqui: por modelo), com média, mínimo, máximo.

    Artigo: "Os três modelos têm médias parecidas. Mas se você tivesse
    medido o Modelo B uma vez só, poderia ter levado para a reunião
    qualquer número entre 14% e 41%."
    """
    # agrupa registros por modelo
    por_modelo: dict[str, list] = defaultdict(list)
    for reg in rodada.registros:
        por_modelo[reg.modelo].append(reg)

    saida: dict[str, dict[str, float]] = {}
    for modelo, regs in por_modelo.items():
        # trata cada registro como uma "execução" e calcula SoM parcial
        # (simplificação didática)
        pesos_modelo: dict[str, float] = defaultdict(float)
        for r in regs:
            from som.etapa5_codificacao import aplicar_regra
            for mid, w in aplicar_regra(r.marcas_citadas, regra).items():
                pesos_modelo[mid] += w
        total = sum(pesos_modelo.values()) or 1.0
        for mid in marca_ids:
            p = pesos_modelo.get(mid, 0.0) / total
            if mid not in saida:
                saida[mid] = {}
            saida[mid][modelo] = p
    return saida


def convergencia(
    forcas: dict[str, float],
    perfis,
    marca_ids: Sequence[str],
    marca_foco: str,
    ns: Sequence[int] = (10, 25, 50, 100, 250, 500, 900),
    seed: int = 7,
) -> list[dict]:
    """
    Demonstra empiricamente por que 900 é o número.

    Roda o simulador com tamanhos de amostra crescentes e compara
    o SoM medido da marca_foco com a verdade assintótica.
    """
    from som.etapa3_modelos import ModeloSimulado, verdade_assintotica
    from som.etapa4_execucao import executar_rodada
    from som.etapa2_prompts import Prompt, PromptSet

    verdade = verdade_assintotica(forcas, perfis, marca_ids, seed=seed)
    p_verdade = verdade.get(marca_foco, 0.0)

    # prompt set mínimo (poucos prompts) para permitir n pequenos na demo
    prompts = [
        Prompt(id=f"p{i}", texto=f"Qual a melhor opção da categoria? ({i})")
        for i in range(5)
    ]
    pset = PromptSet(nome="conv", prompts=prompts)

    # um único modelo na demo de convergência para controlar n com precisão
    perfil0 = perfis[0]
    modelo = ModeloSimulado(perfil0, forcas, seed=seed)

    linhas = []
    for n_alvo in ns:
        # n_exec ≈ n_alvo / n_prompts  (1 modelo)
        n_exec = max(1, math.ceil(n_alvo / len(prompts)))
        rodada = executar_rodada([modelo], pset, marca_ids, n_execucoes=n_exec)
        resultados = som_de_rodada(rodada, marca_ids)
        medido = next((r.som for r in resultados if r.marca_id == marca_foco), 0.0)
        erro = medido - p_verdade
        total_mencoes = sum(r.mencoes for r in resultados) or 1
        lo, hi = intervalo_wilson(medido * total_mencoes, total_mencoes)
        margem = (hi - lo) / 2
        linhas.append(
            {
                "n": rodada.n,
                "som_medido": medido,
                "verdade": p_verdade,
                "erro": erro,
                "margem": margem,
                "dentro": abs(erro) <= margem + 1e-9,
            }
        )
    return linhas


def erro_de_recuperacao(
    resultados: Sequence[ResultadoMarca],
    verdade: dict[str, float],
) -> list[dict]:
    """
    Compara o valor medido com a verdade (só possível no modo simulado).
    Coração didático do projeto.
    """
    linhas = []
    for r in resultados:
        v = verdade.get(r.marca_id, 0.0)
        erro = r.som - v
        contem = r.ic_inferior <= v <= r.ic_superior
        linhas.append(
            {
                "marca": r.marca_id,
                "medido": r.som,
                "verdade": v,
                "erro": erro,
                "ic_contem": contem,
            }
        )
    return linhas
