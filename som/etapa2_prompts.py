"""
Artigo 3, primeira decisão antes da conta:

"Se você mede em janeiro perguntando 'melhor CRM para pequenas empresas'
e em abril perguntando 'qual CRM tem melhor suporte', os dois números
não são comparáveis. Você mudou o teste, não a marca."

"A lista de perguntas precisa ser escrita uma vez, congelada, e repetida
igual em todas as medições. No jargão da área isso se chama prompt set
congelado."

Aqui o congelamento não é figura de linguagem: geramos um hash SHA-256
dos prompts. Se alguém editar uma pergunta, verificar_congelamento()
levanta erro e a quebra da série fica visível em vez de silenciosa.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

Intencao = Literal["exploratoria", "comparativa", "sintese", "outra"]


@dataclass
class Prompt:
    id: str
    texto: str
    intencao: Intencao = "outra"


@dataclass
class PromptSet:
    """
    Conjunto de prompts congelado.

    Artigo: "Depois de escrito, o conjunto não muda. Se precisar
    acrescentar perguntas, comece uma série nova em paralelo."
    """

    nome: str
    prompts: list[Prompt]
    hash_congelamento: str = field(default="", repr=False)
    versao: str = "1"

    def __post_init__(self) -> None:
        if not self.prompts:
            raise ValueError("PromptSet precisa de pelo menos um prompt")
        if not self.hash_congelamento:
            self.hash_congelamento = self._calcular_hash()

    def _calcular_hash(self) -> str:
        """Hash determinístico do conteúdo (ordem e texto dos prompts)."""
        payload = [
            {"id": p.id, "texto": p.texto, "intencao": p.intencao}
            for p in self.prompts
        ]
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verificar_congelamento(self) -> None:
        """
        Levanta RuntimeError se o conteúdo atual não bater com o hash
        gravado. Isso torna a quebra de série explícita.
        """
        atual = self._calcular_hash()
        if atual != self.hash_congelamento:
            raise RuntimeError(
                "Prompt set foi alterado após o congelamento.\n"
                f"Hash esperado : {self.hash_congelamento[:16]}…\n"
                f"Hash atual    : {atual[:16]}…\n"
                "Crie um arquivo v2 e inicie uma série paralela em vez "
                "de editar o conjunto original."
            )

    @property
    def n(self) -> int:
        return len(self.prompts)

    def por_intencao(self) -> dict[str, list[Prompt]]:
        grupos: dict[str, list[Prompt]] = {}
        for p in self.prompts:
            grupos.setdefault(p.intencao, []).append(p)
        return grupos

    @classmethod
    def de_yaml(cls, caminho: str | Path) -> "PromptSet":
        caminho = Path(caminho)
        with caminho.open(encoding="utf-8") as f:
            dados = yaml.safe_load(f)
        prompts = [
            Prompt(
                id=p["id"],
                texto=p["texto"],
                intencao=p.get("intencao", "outra"),
            )
            for p in dados["prompts"]
        ]
        return cls(
            nome=dados.get("nome", caminho.stem),
            prompts=prompts,
            hash_congelamento=dados.get("hash_congelamento", ""),
            versao=str(dados.get("versao", "1")),
        )

    def para_yaml(self, caminho: str | Path) -> None:
        """Grava o conjunto (incluindo o hash) para persistência."""
        caminho = Path(caminho)
        dados = {
            "nome": self.nome,
            "versao": self.versao,
            "hash_congelamento": self.hash_congelamento,
            "prompts": [
                {
                    "id": p.id,
                    "texto": p.texto,
                    "intencao": p.intencao,
                }
                for p in self.prompts
            ],
        }
        with caminho.open("w", encoding="utf-8") as f:
            yaml.safe_dump(dados, f, allow_unicode=True, sort_keys=False)
