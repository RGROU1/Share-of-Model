"""
Artigo 3, etapa 4:

"Executar em rodadas controladas. Múltiplas execuções por pergunta,
dentro de uma janela de tempo definida, com registro de data e versão.
Sem esse registro, quando a série der um salto você não terá como saber
se o mercado mudou ou se o modelo foi atualizado."

Cada execução vira uma linha com data, modelo, versão, prompt e hash
do conjunto. É um livro-razão. Sem ele, o número não é auditável.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence

from som.etapa2_prompts import PromptSet
from som.etapa3_modelos import ModeloBase, Resposta


@dataclass
class RegistroExecucao:
    """Uma linha do livro-razão."""

    timestamp: str
    modelo: str
    versao: str
    prompt_id: str
    prompt_hash_set: str
    marcas_citadas: list[str]
    texto: str = ""


@dataclass
class Rodada:
    """
    Conjunto de execuções de uma medição.
    """

    registros: list[RegistroExecucao] = field(default_factory=list)
    inicio: str = ""
    fim: str = ""

    def adicionar(self, reg: RegistroExecucao) -> None:
        self.registros.append(reg)

    @property
    def n(self) -> int:
        return len(self.registros)


def executar_rodada(
    modelos: Sequence[ModeloBase],
    prompt_set: PromptSet,
    marca_ids: Sequence[str],
    n_execucoes: int = 2,
) -> Rodada:
    """
    Roda n_execucoes de cada combinação (modelo × prompt).

    Artigo: "O número de execuções não é arbitrário: sai do cálculo
    amostral."
    """
    prompt_set.verificar_congelamento()

    rodada = Rodada()
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rodada.inicio = agora

    for modelo in modelos:
        for _ in range(n_execucoes):
            for prompt in prompt_set.prompts:
                resp: Resposta = modelo.responder(
                    prompt.id,
                    prompt.texto,
                    marca_ids,
                )
                reg = RegistroExecucao(
                    timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    modelo=resp.modelo,
                    versao=resp.versao,
                    prompt_id=resp.prompt_id,
                    prompt_hash_set=prompt_set.hash_congelamento,
                    marcas_citadas=list(resp.marcas_citadas),
                    texto=resp.texto,
                )
                rodada.adicionar(reg)

    rodada.fim = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return rodada
