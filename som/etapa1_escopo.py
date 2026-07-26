"""
Artigo 3, etapa 1 do protocolo:

"Definir a categoria e o conjunto competitivo. Quem são os concorrentes
que contam e quais intenções de busca importam. Parece óbvio e não é:
escopo largo demais dilui o indicador, porque você passa a dividir por
um denominador cheio de marcas que ninguém consideraria de verdade."

O trabalho invisível aqui é a resolução de entidades: o modelo pode
escrever "Salesforce", "salesforce.com" ou "SFDC" para a mesma marca.
Sem lista de variantes, você subconta.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


@dataclass
class Marca:
    """Uma marca com todas as variantes de nome que os modelos podem usar."""

    id: str
    nome: str
    aliases: list[str] = field(default_factory=list)

    def todas_variantes(self) -> list[str]:
        return [self.nome] + list(self.aliases)


@dataclass
class Escopo:
    """
    Define a categoria e o conjunto competitivo.

    Artigo: "Escopo largo demais dilui o indicador."
    O método alerta_diluicao() avisa quando passa de 12 marcas.
    """

    categoria: str
    marcas: list[Marca]
    descricao: str = ""

    def __post_init__(self) -> None:
        if not self.marcas:
            raise ValueError("Escopo precisa de pelo menos uma marca")

    @property
    def ids(self) -> list[str]:
        return [m.id for m in self.marcas]

    def resolver(self, texto: str) -> str | None:
        """
        Tenta mapear um trecho de texto para o id de uma marca.
        Comparação case-insensitive, busca por palavra inteira ou alias.
        """
        texto_lower = texto.lower()
        for marca in self.marcas:
            for variante in marca.todas_variantes():
                v = variante.lower()
                # evita substring acidental (ex.: "force" dentro de outra palavra)
                if v in texto_lower:
                    # checagem simples de fronteira
                    idx = texto_lower.find(v)
                    antes = texto_lower[idx - 1] if idx > 0 else " "
                    depois = (
                        texto_lower[idx + len(v)]
                        if idx + len(v) < len(texto_lower)
                        else " "
                    )
                    if not antes.isalnum() and not depois.isalnum():
                        return marca.id
        return None

    def resolver_lista(self, textos: Iterable[str]) -> list[str]:
        """Resolve uma lista de trechos e devolve ids únicos na ordem de aparição."""
        vistos: list[str] = []
        for t in textos:
            mid = self.resolver(t)
            if mid and mid not in vistos:
                vistos.append(mid)
        return vistos

    def alerta_diluicao(self, limite: int = 12) -> str | None:
        """
        Artigo: "Escopo largo demais dilui o indicador."
        Retorna mensagem de alerta se o número de marcas passar do limite.
        """
        n = len(self.marcas)
        if n > limite:
            return (
                f"Atenção: escopo com {n} marcas (limite sugerido: {limite}). "
                "Escopo largo demais dilui o indicador."
            )
        return None

    @classmethod
    def de_yaml(cls, caminho: str | Path) -> "Escopo":
        caminho = Path(caminho)
        with caminho.open(encoding="utf-8") as f:
            dados = yaml.safe_load(f)
        marcas = [
            Marca(
                id=m["id"],
                nome=m["nome"],
                aliases=m.get("aliases", []),
            )
            for m in dados["marcas"]
        ]
        return cls(
            categoria=dados["categoria"],
            marcas=marcas,
            descricao=dados.get("descricao", ""),
        )
