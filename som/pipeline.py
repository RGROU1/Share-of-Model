"""
Orquestra as seis etapas do protocolo em uma única execução.

Artigo 3: "A sequência abaixo é uma compilação: reunimos o que as fontes
disponíveis propõem, organizamos numa ordem executável e explicitamos
o risco de cada etapa."
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from som.amostragem import distribuir, tamanho_amostra
from som.etapa1_escopo import Escopo
from som.etapa2_prompts import PromptSet
from som.etapa3_modelos import (
    ModeloSimulado,
    PerfilModelo,
    verdade_assintotica,
)
from som.etapa4_execucao import Rodada, executar_rodada
from som.etapa5_codificacao import RegraContagem
from som.etapa6_calculo import (
    ResultadoMarca,
    convergencia,
    erro_de_recuperacao,
    som_de_rodada,
)


# --- dados sintéticos do demo (marcas fictícias de propósito) ---------------

FORCAS_DEMO = {
    "marca_a": 0.42,
    "marca_b": 0.28,
    "marca_c": 0.18,
    "marca_d": 0.12,
}

PERFIS_DEMO = [
    PerfilModelo("Modelo-Alpha", "2026.1", verbosidade=3.2, ruido=0.12),
    PerfilModelo("Modelo-Beta", "2026.1", verbosidade=2.4, ruido=0.22),
    PerfilModelo("Modelo-Gamma", "2026.1", verbosidade=3.8, ruido=0.10),
    PerfilModelo("Modelo-Delta", "2026.1", verbosidade=2.8, ruido=0.18),
]


@dataclass
class ResultadoPipeline:
    escopo: Escopo
    prompt_set: PromptSet
    rodada: Rodada
    resultados: list[ResultadoMarca]
    verdade: dict[str, float]
    recuperacao: list[dict]
    convergencia: list[dict]
    n_execucoes: int
    regra: RegraContagem


def carregar_escopo(caminho: str | Path | None = None) -> Escopo:
    if caminho is None:
        caminho = Path(__file__).resolve().parent.parent / "config" / "categoria_crm.yaml"
    return Escopo.de_yaml(caminho)


def carregar_prompts(caminho: str | Path | None = None) -> PromptSet:
    if caminho is None:
        caminho = Path(__file__).resolve().parent.parent / "prompts" / "crm_v1.yaml"
    return PromptSet.de_yaml(caminho)


def rodar_demo(
    n_execucoes: int | None = None,
    regra: RegraContagem = RegraContagem.PRESENCA,
) -> ResultadoPipeline:
    """
    Pipeline completo em modo simulado.
    Sem chave de API. Sem custo. Roda em segundos.
    """
    escopo = carregar_escopo()
    prompt_set = carregar_prompts()
    prompt_set.verificar_congelamento()

    alerta = escopo.alerta_diluicao()
    if alerta:
        print(f"[aviso] {alerta}")

    marca_ids = escopo.ids

    if n_execucoes is None:
        n_execucoes = distribuir(prompt_set.n, len(PERFIS_DEMO))

    modelos = [
        ModeloSimulado(perfil, FORCAS_DEMO, seed=100 + i)
        for i, perfil in enumerate(PERFIS_DEMO)
    ]

    rodada = executar_rodada(modelos, prompt_set, marca_ids, n_execucoes=n_execucoes)
    resultados = som_de_rodada(rodada, marca_ids, regra=regra)

    verdade = verdade_assintotica(FORCAS_DEMO, PERFIS_DEMO, marca_ids)
    recuperacao = erro_de_recuperacao(resultados, verdade)

    # convergência focada na segunda marca (challenger típico)
    conv = convergencia(
        FORCAS_DEMO,
        PERFIS_DEMO,
        marca_ids,
        marca_foco="marca_b",
        seed=21,
    )

    return ResultadoPipeline(
        escopo=escopo,
        prompt_set=prompt_set,
        rodada=rodada,
        resultados=resultados,
        verdade=verdade,
        recuperacao=recuperacao,
        convergencia=conv,
        n_execucoes=n_execucoes,
        regra=regra,
    )
