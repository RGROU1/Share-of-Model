"""Trava os números publicados no artigo."""

from som.amostragem import distribuir, tamanho_amostra


def test_tamanho_amostra_artigo():
    # p=0.30, margem=0.03, 95% → ≈897
    n = tamanho_amostra(p=0.30, margem=0.03, confianca=0.95)
    assert n == 897, f"Esperado 897, obtido {n}"


def test_distribuir_artigo():
    # 120 prompts × 4 modelos → 2 execuções (897/480 ≈ 1.87 → 2)
    assert distribuir(120, 4) == 2
