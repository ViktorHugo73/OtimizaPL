import csv
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from experiments.gerador import gerar_factivel_limitado
from motor import SimplexDuasFases
from validacao import resolver_highs, comparar_resultados


BASE = Path(__file__).resolve().parent

PASTA_RESULTADOS = BASE / "results"

PASTA_RESULTADOS.mkdir(
    parents=True,
    exist_ok=True
)


CONFIGURACOES = [
    (5, 10),
    (10, 20),
    (20, 40),
    (50, 100),
    (100, 200),
]


REPETICOES_INSTANCIAS = 10

REPETICOES_TEMPO = 5


def medir_tempo(funcao, repeticoes=5):

    tempos = []

    ultimo_resultado = None

    for _ in range(repeticoes):

        inicio = perf_counter_ns()

        ultimo_resultado = funcao()

        fim = perf_counter_ns()

        tempo_ms = (
            fim - inicio
        ) / 1_000_000

        tempos.append(
            tempo_ms
        )

    return (
        ultimo_resultado,
        median(tempos)
    )


def main():

    solver = SimplexDuasFases()

    resultados = []

    total = 0

    aprovados = 0

    contador = 1

    for n_variaveis, n_restricoes in CONFIGURACOES:

        print()
        print(
            f"===== "
            f"{n_variaveis} variáveis / "
            f"{n_restricoes} restrições "
            f"====="
        )

        for repeticao in range(
            REPETICOES_INSTANCIAS
        ):

            identificador = (
                f"ESC_{contador:03d}"
            )

            seed = (
                20000
                +
                contador
            )

            problema = gerar_factivel_limitado(

                identificador=identificador,

                n_variaveis=n_variaveis,

                n_restricoes_aleatorias=(
                    n_restricoes
                ),

                seed=seed,

                objetivo=(
                    "min"
                    if contador % 2 == 0
                    else "max"
                )
            )

            total += 1

            # ==============================================
            # MOTOR PRÓPRIO
            # ==============================================

            def executar_proprio():

                return solver.resolver(

                    problema.A,

                    problema.b,

                    problema.c,

                    problema.operadores,

                    problema.objetivo
                )

            proprio, tempo_proprio = medir_tempo(

                executar_proprio,

                REPETICOES_TEMPO
            )

            # ==============================================
            # HIGHS
            # ==============================================

            def executar_highs():

                return resolver_highs(

                    problema.A,

                    problema.b,

                    problema.c,

                    problema.operadores,

                    problema.objetivo
                )

            referencia, tempo_highs = medir_tempo(

                executar_highs,

                REPETICOES_TEMPO
            )

            # ==============================================
            # COMPARAÇÃO
            # ==============================================

            comparacao = comparar_resultados(

                proprio,

                referencia,

                problema.A,

                problema.b,

                problema.operadores
            )

            if comparacao.aprovado:

                aprovados += 1

            resultados.append({

                "id":
                    identificador,

                "seed":
                    seed,

                "n_variaveis":
                    n_variaveis,

                "n_restricoes":
                    problema.n_restricoes,

                "objetivo":
                    problema.objetivo,

                "status_proprio":
                    proprio.status,

                "status_highs":
                    referencia.status,

                "erro_z_absoluto":
                    comparacao.erro_z_absoluto,

                "erro_z_relativo":
                    comparacao.erro_z_relativo,

                "violacao_maxima":
                    comparacao.violacao_maxima,

                "iteracoes_fase1":
                    proprio.iteracoes_fase1,

                "iteracoes_fase2":
                    proprio.iteracoes_fase2,

                "iteracoes_highs":
                    referencia.iteracoes,

                "tempo_proprio_ms":
                    tempo_proprio,

                "tempo_highs_ms":
                    tempo_highs,

                "aprovado":
                    comparacao.aprovado
            })

            print(

                f"{identificador} | "

                f"{proprio.status} / "
                f"{referencia.status} | "

                f"Simplex="
                f"{tempo_proprio:.3f} ms | "

                f"HiGHS="
                f"{tempo_highs:.3f} ms | "

                f"OK="
                f"{comparacao.aprovado}"
            )

            contador += 1

    caminho = (
        PASTA_RESULTADOS
        /
        "resultados_escala.csv"
    )

    with caminho.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        writer = csv.DictWriter(

            arquivo,

            fieldnames=resultados[0].keys()
        )

        writer.writeheader()

        writer.writerows(
            resultados
        )

    print()

    print("=" * 70)

    print(
        f"Aprovados: "
        f"{aprovados}/{total}"
    )

    print(
        f"Arquivo: {caminho}"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()