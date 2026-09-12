import csv
import json
import platform
import sys

from pathlib import Path

import numpy as np
import scipy


from experiments.gerador import (
    gerar_factivel_limitado,
    gerar_factivel_misto,
    gerar_inviavel,
    gerar_ilimitado,
)

from validacao import executar_comparacao


BASE = Path(__file__).resolve().parent

PASTA_INSTANCIAS = (
    BASE
    /
    "instances"
)

PASTA_RESULTADOS = (
    BASE
    /
    "results"
)


PASTA_INSTANCIAS.mkdir(
    parents=True,
    exist_ok=True
)

PASTA_RESULTADOS.mkdir(
    parents=True,
    exist_ok=True
)


def gerar_bateria():

    problemas = []

    contador = 1

    # ========================================================
    # 35 FACTÍVEIS LIMITADOS
    # ========================================================

    for i in range(35):

        n = (
            2
            +
            (i % 10)
        )

        m = (
            3
            +
            (i % 15)
        )

        problema = gerar_factivel_limitado(

            identificador=f"P{contador:03d}",

            n_variaveis=n,

            n_restricoes_aleatorias=m,

            seed=3471 + contador,

            objetivo=(
                "min"
                if contador % 2 == 0
                else "max"
            )
        )

        problemas.append(
            problema
        )

        contador += 1


    # ========================================================
    # 35 FACTÍVEIS MISTOS
    # ========================================================

    for i in range(35):

        n = (
            2
            +
            (i % 8)
        )

        m = (
            3
            +
            (i % 12)
        )

        problema = gerar_factivel_misto(

            identificador=f"P{contador:03d}",

            n_variaveis=n,

            n_restricoes_aleatorias=m,

            seed=7000 + contador,

            objetivo=(
                "min"
                if contador % 2 == 0
                else "max"
            )
        )

        problemas.append(
            problema
        )

        contador += 1


    # ========================================================
    # 15 INVIÁVEIS
    # ========================================================

    for i in range(15):

        problema = gerar_inviavel(

            identificador=f"P{contador:03d}",

            n_variaveis=(
                2
                +
                (i % 10)
            ),

            seed=10000 + contador
        )

        problemas.append(
            problema
        )

        contador += 1


    # ========================================================
    # 15 ILIMITADOS
    # ========================================================

    for i in range(15):

        problema = gerar_ilimitado(

            identificador=f"P{contador:03d}",

            n_variaveis=(
                2
                +
                (i % 10)
            ),

            seed=13000 + contador
        )

        problemas.append(
            problema
        )

        contador += 1


    return problemas


def salvar_instancia(
    problema
):

    caminho = (
        PASTA_INSTANCIAS
        /
        f"{problema.id}.json"
    )

    with caminho.open(
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(

            problema.para_dict(),

            arquivo,

            indent=2,

            ensure_ascii=False
        )


def salvar_ambiente():

    ambiente = {

        "python":
            sys.version,

        "platforma":
            platform.platform(),

        "processador":
            platform.processor(),

        "numpy":
            np.__version__,

        "scipy":
            scipy.__version__,

        "quantidade_instancias":
            100,

        "repeticoes_tempo":
            5,
    }


    caminho = (
        PASTA_RESULTADOS
        /
        "ambiente_v2.json"
    )


    with caminho.open(
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(

            ambiente,

            arquivo,

            indent=2,

            ensure_ascii=False
        )


def main():

    problemas = gerar_bateria()

    resultados = []

    aprovados = 0


    for problema in problemas:

        salvar_instancia(
            problema
        )


        benchmark = executar_comparacao(

            problema,

            repeticoes=5
        )


        proprio = (
            benchmark.proprio
        )

        referencia = (
            benchmark.referencia
        )

        comparacao = (
            benchmark.comparacao
        )


        if comparacao.aprovado:

            aprovados += 1


        linha = {

            "id":
                problema.id,

            "classe":
                problema.classe,

            "seed":
                problema.seed,

            "n_variaveis":
                problema.n_variaveis,

            "n_restricoes":
                problema.n_restricoes,

            "objetivo":
                problema.objetivo,

            "status_proprio":
                proprio.status,

            "status_highs":
                referencia.status,

            "status_igual":
                comparacao.status_igual,

            "z_proprio":
                proprio.valor_objetivo,

            "z_highs":
                referencia.valor_objetivo,

            "erro_z_absoluto":
                comparacao.erro_z_absoluto,

            "erro_z_relativo":
                comparacao.erro_z_relativo,

            "erro_x_maximo":
                comparacao.erro_x_maximo,

            "violacao_maxima":
                comparacao.violacao_maxima,

            "iteracoes_fase1":
                proprio.iteracoes_fase1,

            "iteracoes_fase2":
                proprio.iteracoes_fase2,

            "iteracoes_highs":
                referencia.iteracoes,

            "tempo_proprio_ms_mediana":
                benchmark.tempo_proprio_ms,

            "tempo_highs_ms_mediana":
                benchmark.tempo_highs_ms,

            "aprovado":
                comparacao.aprovado,
        }


        resultados.append(
            linha
        )


        print(

            f"{problema.id} | "

            f"{problema.classe:20} | "

            f"{proprio.status:10} / "

            f"{referencia.status:10} | "

            f"aprovado={comparacao.aprovado}"
        )


    caminho_csv = (
        PASTA_RESULTADOS
        /
        "resultados_v2.csv"
    )


    if resultados:

        with caminho_csv.open(

            "w",

            newline="",

            encoding="utf-8"

        ) as arquivo:

            writer = csv.DictWriter(

                arquivo,

                fieldnames=(
                    resultados[0]
                    .keys()
                )
            )

            writer.writeheader()

            writer.writerows(
                resultados
            )


    salvar_ambiente()


    print()

    print(
        "=" * 60
    )

    print(
        f"Aprovados: "
        f"{aprovados}/"
        f"{len(problemas)}"
    )

    print(
        f"CSV: {caminho_csv}"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":

    main()