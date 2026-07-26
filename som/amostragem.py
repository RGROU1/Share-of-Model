"""
Artigo 3, seção "Quantas execuções são necessárias":

"Share of Model é uma proporção, exatamente como intenção de voto.
O cálculo é o mesmo."

"Para uma marca com participação esperada em torno de 30%, querendo
margem de 3 pontos para mais ou para menos e 95% de confiança,
são necessárias aproximadamente 900 observações válidas."

Ressalva do artigo (e deste módulo): a conta pressupõe observações
independentes. Rodar a mesma pergunta duas vezes produz resultados
mais parecidos do que rodar duas perguntas diferentes, o que reduz
o número efetivo de observações. Trate 900 como piso e não como alvo.
"""

from __future__ import annotations

import math


def tamanho_amostra(
    p: float = 0.30,
    margem: float = 0.03,
    confianca: float = 0.95,
) -> int:
    """
    n = z² · p(1−p) / E²

    Retorna o tamanho de amostra necessário para estimar uma proporção
    com a margem e confiança desejadas.

    Valores padrão reproduzem o número publicado no artigo (≈897).
    """
    if not 0 < p < 1:
        raise ValueError("p deve estar entre 0 e 1 (exclusive)")
    if margem <= 0:
        raise ValueError("margem deve ser positiva")
    if not 0 < confianca < 1:
        raise ValueError("confiança deve estar entre 0 e 1")

    # z para 95% ≈ 1.96; para outros níveis usamos aproximação normal
    z = {
        0.90: 1.645,
        0.95: 1.960,
        0.99: 2.576,
    }.get(round(confianca, 2), 1.960)

    n = (z ** 2 * p * (1 - p)) / (margem ** 2)
    return math.ceil(n)


def distribuir(n_prompts: int, n_modelos: int, n_alvo: int | None = None) -> int:
    """
    Calcula quantas execuções por combinação (prompt × modelo) são
    necessárias para atingir o n total de observações.

    Artigo: "Com 120 perguntas fixas rodadas em 4 modelos, isso significa
    cerca de duas execuções por combinação."
    """
    if n_alvo is None:
        n_alvo = tamanho_amostra()
    combinacoes = n_prompts * n_modelos
    if combinacoes == 0:
        raise ValueError("n_prompts e n_modelos devem ser > 0")
    return math.ceil(n_alvo / combinacoes)
