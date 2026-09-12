import csv

from collections import defaultdict
from pathlib import Path
from statistics import mean, median


BASE = Path(__file__).resolve().parent

ARQUIVO = (
    BASE
    /
    "results"
    /
    "resultados_escala.csv"
)


def converter_float(valor):

    if valor in (
        "",
        "None",
        None
    ):
        return None

    return float(valor)


def main():

    grupos = defaultdict(list)

    with ARQUIVO.open(
        "r",
        encoding="utf-8"
    ) as arquivo:

        reader = csv.DictReader(
            arquivo
        )

        for linha in reader:

            n = int(
                linha["n_variaveis"]
            )

            grupos[n].append(
                linha
            )

    print()

    print(
        "RESUMO DO TESTE DE ESCALA"
    )

    print(
        "=" * 85
    )

    print(
        f"{'N':>6} | "
        f"{'Casos':>6} | "
        f"{'Simplex med.':>14} | "
        f"{'HiGHS med.':>12} | "
        f"{'Erro Z máx.':>12} | "
        f"{'Aprovados':>9}"
    )

    print(
        "-" * 85
    )

    for n in sorted(
        grupos.keys()
    ):

        linhas = grupos[n]

        tempos_proprio = [

            float(
                linha[
                    "tempo_proprio_ms"
                ]
            )

            for linha in linhas
        ]

        tempos_highs = [

            float(
                linha[
                    "tempo_highs_ms"
                ]
            )

            for linha in linhas
        ]

        erros = [

            converter_float(
                linha[
                    "erro_z_relativo"
                ]
            )

            for linha in linhas
        ]

        erros = [

            erro

            for erro in erros

            if erro is not None
        ]

        aprovados = sum(

            linha["aprovado"].lower()
            ==
            "true"

            for linha in linhas
        )

        erro_maximo = (

            max(erros)

            if erros

            else 0.0
        )

        print(

            f"{n:>6} | "

            f"{len(linhas):>6} | "

            f"{median(tempos_proprio):>14.4f} | "

            f"{median(tempos_highs):>12.4f} | "

            f"{erro_maximo:>12.3e} | "

            f"{aprovados:>3}/"
            f"{len(linhas):<5}"
        )


if __name__ == "__main__":

    main()