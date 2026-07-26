"""
Artigo 3, etapa 5:

"Modelos verbosos citam mais marcas por resposta que modelos concisos,
e isso distorce a comparação se você não ajustar."

"Ser citada de passagem e ser recomendada como primeira escolha não
são a mesma coisa. Você precisa decidir se conta as duas, se conta
só a recomendação explícita, ou se dá pesos diferentes. Não existe
resposta certa, existe resposta escrita."

"Peça a duas pessoas para classificar as mesmas cinquenta respostas
e veja se elas concordam. Se não concordarem, a regra está ambígua."
"""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Sequence

from som.etapa4_execucao import RegistroExecucao, Rodada


class RegraContagem(Enum):
    """As três regras que o artigo deixa em aberto."""

    PRESENCA = "presenca"      # apareceu → conta 1
    PRIMEIRA = "primeira"      # só a primeira citada conta 1
    PONDERADA = "ponderada"    # 1.0 para a primeira, 0.5 para as demais


def aplicar_regra(
    marcas_citadas: Sequence[str],
    regra: RegraContagem,
) -> dict[str, float]:
    """
    Devolve {marca_id: peso} para uma única resposta.
    """
    pesos: dict[str, float] = {}
    if not marcas_citadas:
        return pesos

    if regra is RegraContagem.PRESENCA:
        for mid in marcas_citadas:
            pesos[mid] = 1.0
    elif regra is RegraContagem.PRIMEIRA:
        pesos[marcas_citadas[0]] = 1.0
    elif regra is RegraContagem.PONDERADA:
        pesos[marcas_citadas[0]] = 1.0
        for mid in marcas_citadas[1:]:
            pesos[mid] = 0.5
    return pesos


def fator_verbosidade(rodada: Rodada) -> dict[str, float]:
    """
    Calcula, por modelo, quantas marcas são citadas em média por resposta
    e devolve o multiplicador que iguala todos à média global.

    Artigo: "Modelos verbosos citam mais marcas por resposta que modelos
    concisos, e isso distorce a comparação se você não ajustar."
    """
    por_modelo: dict[str, list[int]] = defaultdict(list)
    for reg in rodada.registros:
        por_modelo[reg.modelo].append(len(reg.marcas_citadas))

    medias = {
        m: (sum(vals) / len(vals) if vals else 1.0)
        for m, vals in por_modelo.items()
    }
    media_global = sum(medias.values()) / len(medias) if medias else 1.0

    # fator = media_global / media_modelo  → modelos falantes recebem fator < 1
    return {
        m: (media_global / med if med > 0 else 1.0)
        for m, med in medias.items()
    }


def codificar_rodada(
    rodada: Rodada,
    regra: RegraContagem = RegraContagem.PRESENCA,
    normalizar_verbosidade: bool = True,
) -> dict[str, float]:
    """
    Agrega os pesos de todas as respostas da rodada.

    Retorna {marca_id: peso_total}.
    O denominador do SoM será a soma desses pesos.
    """
    fatores = fator_verbosidade(rodada) if normalizar_verbosidade else {}
    totais: dict[str, float] = defaultdict(float)

    for reg in rodada.registros:
        pesos = aplicar_regra(reg.marcas_citadas, regra)
        fator = fatores.get(reg.modelo, 1.0)
        for mid, w in pesos.items():
            totais[mid] += w * fator

    return dict(totais)


def concordancia(
    classificacoes_a: Sequence[Sequence[str]],
    classificacoes_b: Sequence[Sequence[str]],
) -> float:
    """
    Concordância simples entre dois avaliadores (proporção de respostas
    em que a lista de marcas extraídas é idêntica).

    Artigo: "Peça a duas pessoas para classificar as mesmas cinquenta
    respostas e veja se elas concordam. Se não concordarem, a regra
    está ambígua."

    Abaixo de 0,80 a regra deve ser revista.
    """
    if len(classificacoes_a) != len(classificacoes_b):
        raise ValueError("As duas listas precisam ter o mesmo tamanho")
    if not classificacoes_a:
        return 1.0

    iguais = sum(
        1
        for a, b in zip(classificacoes_a, classificacoes_b)
        if list(a) == list(b)
    )
    return iguais / len(classificacoes_a)
