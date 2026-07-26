"""
Saída em texto puro, sem dependência externa.

Artigo 3: "Sempre com a média, a dispersão e o número de observações.
Um número solto não sustenta decisão nenhuma."
"""

from __future__ import annotations

from som.etapa5_codificacao import RegraContagem
from som.pipeline import ResultadoPipeline


def _pct(x: float) -> str:
    return f"{x * 100:5.1f}%"


def _pp(x: float) -> str:
    sinal = "+" if x >= 0 else ""
    return f"{sinal}{x * 100:4.1f}p"


def imprimir_relatorio(res: ResultadoPipeline) -> None:
    print("=" * 78)
    print("SHARE OF MODEL — relatório de medição (modo simulado)")
    print("=" * 78)
    print(f"Categoria     : {res.escopo.categoria}")
    print(f"Marcas        : {', '.join(m.nome for m in res.escopo.marcas)}")
    print(f"Prompt set    : {res.prompt_set.nome} (v{res.prompt_set.versao})")
    print(f"Hash          : {res.prompt_set.hash_congelamento[:16]}…")
    print(f"Prompts       : {res.prompt_set.n}")
    print(f"Modelos       : {len(set(r.modelo for r in res.rodada.registros))}")
    print(f"Execuções/comb: {res.n_execucoes}")
    print(f"Observações   : {res.rodada.n}")
    print(f"Regra         : {res.regra.value}")
    print()

    print("-" * 78)
    print("RESULTADO CONSOLIDADO")
    print("-" * 78)
    print(f"{'MARCA':<12} {'MENÇÕES':>10} {'SoM':>8} {'IC 95%':>18} {'n':>6}")
    print("-" * 78)
    for r in sorted(res.resultados, key=lambda x: -x.som):
        nome = next(m.nome for m in res.escopo.marcas if m.id == r.marca_id)
        ic = f"[{_pct(r.ic_inferior)} – {_pct(r.ic_superior)}]"
        print(
            f"{nome:<12} {r.mencoes:10.1f} {_pct(r.som):>8} {ic:>18} {r.n_observacoes:6d}"
        )
    print()

    print("-" * 78)
    print("O PIPELINE ACERTOU? (só possível no modo simulado)")
    print("-" * 78)
    print(f"{'MARCA':<12} {'MEDIDO':>8} {'VERDADE':>8} {'ERRO':>8} {'IC CONTÉM?':>10}")
    print("-" * 78)
    acertos = 0
    for linha in res.recuperacao:
        nome = next(m.nome for m in res.escopo.marcas if m.id == linha["marca"])
        contem = "sim" if linha["ic_contem"] else "NÃO"
        if linha["ic_contem"]:
            acertos += 1
        print(
            f"{nome:<12} {_pct(linha['medido']):>8} {_pct(linha['verdade']):>8} "
            f"{_pp(linha['erro']):>8} {contem:>10}"
        )
    print("-" * 78)
    print(
        f"O intervalo de confiança conteve o valor verdadeiro em "
        f"{acertos}/{len(res.recuperacao)} marcas."
    )
    print()

    print("-" * 78)
    print("CONVERGÊNCIA: quantas execuções bastam?")
    print("-" * 78)
    print(f"{'n':>6} {'SoM MEDIDO':>12} {'ERRO':>8} {'MARGEM':>8} {'DENTRO?':>8}")
    print("-" * 78)
    for c in res.convergencia:
        dentro = "sim" if c["dentro"] else "não"
        print(
            f"{c['n']:6d} {_pct(c['som_medido']):>12} {_pp(c['erro']):>8} "
            f"{_pct(c['margem']):>8} {dentro:>8}"
        )
    print()
    print(
        "Com poucas execuções a margem é enorme: o número não serve para decidir.\n"
        "Com ~900 observações a margem cai para a ordem de 2–3 pontos."
    )
    print("=" * 78)


def imprimir_regras(resultados_por_regra: dict[RegraContagem, list]) -> None:
    print("=" * 78)
    print("COMPARAÇÃO DAS TRÊS REGRAS DE CONTAGEM")
    print("=" * 78)
    print(
        "Artigo 3: 'Ser citada de passagem e ser recomendada como primeira\n"
        "escolha não são a mesma coisa. Não existe resposta certa, existe\n"
        "resposta escrita.'"
    )
    print()

    # cabeçalho
    regras = list(resultados_por_regra.keys())
    header = f"{'MARCA':<12}"
    for reg in regras:
        header += f" {reg.value.upper():>12}"
    print(header)
    print("-" * len(header))

    # assume mesma ordem de marcas
    marcas = [r.marca_id for r in resultados_por_regra[regras[0]]]
    for mid in marcas:
        linha = f"{mid:<12}"
        for reg in regras:
            som = next(r.som for r in resultados_por_regra[reg] if r.marca_id == mid)
            linha += f" {_pct(som):>12}"
        print(linha)
    print("=" * 78)
