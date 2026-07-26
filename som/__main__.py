"""
CLI do Share of Model.

Comandos:
  python -m som demo [n_execucoes]
  python -m som regras
"""

from __future__ import annotations

import sys

from som.etapa5_codificacao import RegraContagem
from som.pipeline import rodar_demo
from som.relatorio import imprimir_relatorio, imprimir_regras


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return

    cmd = argv[0]

    if cmd == "demo":
        n_exec = int(argv[1]) if len(argv) > 1 else None
        res = rodar_demo(n_execucoes=n_exec)
        imprimir_relatorio(res)
        return

    if cmd == "regras":
        resultados = {}
        for regra in RegraContagem:
            res = rodar_demo(n_execucoes=2, regra=regra)
            resultados[regra] = res.resultados
        imprimir_regras(resultados)
        return

    print(f"Comando desconhecido: {cmd}")
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
