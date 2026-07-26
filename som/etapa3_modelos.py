"""
Artigo 3, etapa 3:

"Escolher a malha de modelos. ChatGPT, Claude, Gemini, Perplexity e
AI Overviews se comportam de forma diferente entre si, e a diferença
entre eles costuma ser maior que a variação dentro de cada um.
Medir em um só modelo produz um retrato parcial."

"A variância entre modelos supera a variância interna. Cross-model
é obrigatório."

Este módulo contém o simulador (para o demo sem API) e o esqueleto
dos adaptadores reais. Os adaptadores estão deliberadamente incompletos:
manter integração com três provedores desatualiza rápido, e código de
integração quebrado engana mais do que ajuda.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class Resposta:
    """Uma resposta gerada por um modelo a um prompt."""

    modelo: str
    versao: str
    prompt_id: str
    marcas_citadas: list[str]  # ids na ordem de aparição
    texto: str = ""


@dataclass
class PerfilModelo:
    """
    Parâmetros do simulador para um modelo.

    - verbosidade: quantas marcas, em média, o modelo cita por resposta
    - ruido: desvio-padrão do ruído gaussiano aplicado às forças (não-determinismo)
    - vies: dict id→multiplicador de força (preferência residual do modelo)
    """

    nome: str
    versao: str
    verbosidade: float = 3.0
    ruido: float = 0.15
    vies: dict[str, float] = field(default_factory=dict)


class ModeloBase(ABC):
    """Interface mínima que qualquer adaptador (real ou simulado) implementa."""

    @abstractmethod
    def responder(self, prompt_id: str, prompt_texto: str, marca_ids: Sequence[str]) -> Resposta:
        ...


class ModeloSimulado(ModeloBase):
    """
    Simulador com forças latentes conhecidas.

    Artigo (implícito no uso didático): só no modo simulado é possível
    comparar o valor medido com a verdade.

    Mecânica:
    1. Cada marca tem uma força latente fixa.
    2. Em cada chamada, aplica-se ruído gaussiano + viés do modelo.
    3. Ordena-se e corta-se nas N primeiras (N ~ Poisson(verbosidade)).
    """

    def __init__(
        self,
        perfil: PerfilModelo,
        forcas: dict[str, float],
        seed: int | None = None,
    ) -> None:
        self.perfil = perfil
        self.forcas = dict(forcas)
        self._rng = random.Random(seed)

    def responder(
        self,
        prompt_id: str,
        prompt_texto: str,
        marca_ids: Sequence[str],
    ) -> Resposta:
        # força efetiva = força latente × viés × (1 + ruído)
        efetivas: list[tuple[str, float]] = []
        for mid in marca_ids:
            base = self.forcas.get(mid, 0.01)
            vies = self.perfil.vies.get(mid, 1.0)
            ruido = self._rng.gauss(0, self.perfil.ruido)
            valor = base * vies * max(0.01, 1.0 + ruido)
            efetivas.append((mid, valor))

        efetivas.sort(key=lambda x: x[1], reverse=True)

        # quantas marcas citar (verbosidade + pequena variação)
        n_citar = max(1, int(round(self._rng.gauss(self.perfil.verbosidade, 0.6))))
        n_citar = min(n_citar, len(efetivas))

        citadas = [mid for mid, _ in efetivas[:n_citar]]

        # texto sintético mínimo (só para legibilidade do log)
        if citadas:
            texto = f"As opções mais indicadas são {', '.join(citadas)}."
        else:
            texto = "Não há recomendações claras para este caso."

        return Resposta(
            modelo=self.perfil.nome,
            versao=self.perfil.versao,
            prompt_id=prompt_id,
            marcas_citadas=citadas,
            texto=texto,
        )


def verdade_assintotica(
    forcas: dict[str, float],
    perfis: Sequence[PerfilModelo],
    marca_ids: Sequence[str],
    n_simulacoes: int = 5000,
    seed: int = 42,
) -> dict[str, float]:
    """
    Estima a participação 'verdadeira' de cada marca no limite de
    muitas execuções, via Monte Carlo.

    Decisão documentada no CLAUDE.md:
    "A verdade do simulador é calculada por Monte Carlo, não pela força
    latente normalizada. O simulador ordena as marcas por força e corta
    nas N primeiras, então a participação resultante não é proporcional
    à força."
    """
    contagem: dict[str, float] = {mid: 0.0 for mid in marca_ids}
    total = 0.0

    rng = random.Random(seed)
    for perfil in perfis:
        modelo = ModeloSimulado(perfil, forcas, seed=rng.randint(0, 10**9))
        for _ in range(n_simulacoes // max(1, len(perfis))):
            resp = modelo.responder("mc", "prompt sintético", marca_ids)
            for mid in resp.marcas_citadas:
                contagem[mid] += 1.0
            total += len(resp.marcas_citadas)

    if total == 0:
        return {mid: 0.0 for mid in marca_ids}
    return {mid: contagem[mid] / total for mid in marca_ids}


# ---------------------------------------------------------------------------
# Esqueleto de adaptadores reais (propositalmente incompletos)
# ---------------------------------------------------------------------------

class ModeloAoVivo(ModeloBase):
    """
    Esqueleto. Implemente responder() para o seu provedor.
    Sempre registre a versão exata do modelo.
    """

    def __init__(self, nome: str, versao: str, api_key: str | None = None) -> None:
        self.nome = nome
        self.versao = versao
        self.api_key = api_key

    def responder(
        self,
        prompt_id: str,
        prompt_texto: str,
        marca_ids: Sequence[str],
    ) -> Resposta:
        raise NotImplementedError(
            "Adaptadores reais estão incompletos de propósito. "
            "Implemente a chamada à API e a extração de menções "
            "antes de usar em produção."
        )
