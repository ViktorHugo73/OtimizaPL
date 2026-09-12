"""Executa comparação em lote entre Simplex próprio e SciPy/HiGHS.

Saídas:
- experiments/results/resultados.csv
- experiments/results/ambiente.json
- experiments/instances/*.json
"""

from __future__ import annotations

import csv
import json
import platform
import statistics
import sys
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import scipy

# Permite executar este arquivo diretamente a partir da raiz do projeto.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from motor import SimplexDuasFases
from validacao import resolver_highs, comparar_resultados
from experiments.gerador import gerar_factível_limitado


PASTA_INSTANCIAS = ROOT / "experiments" / "instances"
PASTA_RESULTADOS = ROOT / "experiments" / "results"
PASTA_INSTANCIAS.mkdir(parents=True, exist_ok=True)
PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)


def medir_ms(funcao, repeticoes=3):
    tempos = []
    ultimo_resultado = None

    for _ in range(repeticoes):
        inicio = perf_counter_ns()
        ultimo_resultado = funcao()
        fim = perf_counter_ns()
        tempos.append((fim - inicio) / 1_000_000.0)

    return ultimo_resultado, statistics.median(tempos)


def salvar_instancia(problema):
    dados = {
        "id": problema.id,
        "seed": problema.seed,
        "objetivo": problema.objetivo,
        "n_variaveis": problema.n_variaveis,
        "n_restricoes": problema.n_restricoes,
        "A": problema.A,
        "b": problema.b,
        "c": problema.c,
        "operadores": problema.operadores,
    }
    caminho = PASTA_INSTANCIAS / f"{problema.id}.json"
    caminho.write_text(json.dumps(dados, indent=2), encoding="utf-8")


def main():
    solver = SimplexDuasFases()

    # 50 instâncias iniciais. O experimento final do TCC pode ser ampliado depois.
    configuracoes = [
        (2, 4, 10),
        (5, 8, 10),
        (8, 12, 10),
        (10, 15, 10),
        (12, 20, 10),
    ]

    linhas = []
    contador = 0

    for n_variaveis, n_restr_aleatorias, quantidade in configuracoes:
        for k in range(quantidade):
            contador += 1
            seed = 3471 + contador
            objetivo = "min" if contador % 2 == 0 else "max"
            identificador = f"P{contador:03d}"

            problema = gerar_factível_limitado(
                identificador=identificador,
                n_variaveis=n_variaveis,
                n_restricoes_aleatorias=n_restr_aleatorias,
                seed=seed,
                objetivo=objetivo,
            )
            salvar_instancia(problema)

            proprio, tempo_proprio_ms = medir_ms(
                lambda: solver.resolver(
                    problema.A,
                    problema.b,
                    problema.c,
                    problema.operadores,
                    problema.objetivo,
                )
            )

            referencia, tempo_highs_ms = medir_ms(
                lambda: resolver_highs(
                    problema.A,
                    problema.b,
                    problema.c,
                    problema.operadores,
                    problema.objetivo,
                )
            )

            comparacao = comparar_resultados(
                proprio,
                referencia,
                problema.A,
                problema.b,
                problema.operadores,
            )

            linhas.append({
                "id": problema.id,
                "seed": problema.seed,
                "n_variaveis": problema.n_variaveis,
                "n_restricoes": problema.n_restricoes,
                "objetivo": problema.objetivo,
                "status_proprio": proprio.status,
                "status_highs": referencia.status,
                "status_igual": comparacao.status_igual,
                "z_proprio": proprio.valor_objetivo,
                "z_highs": referencia.valor_objetivo,
                "erro_z_absoluto": comparacao.erro_z_absoluto,
                "erro_z_relativo": comparacao.erro_z_relativo,
                "erro_x_maximo": comparacao.erro_x_maximo,
                "violacao_maxima": comparacao.violacao_maxima,
                "iteracoes_fase1": proprio.iteracoes_fase1,
                "iteracoes_fase2": proprio.iteracoes_fase2,
                "iteracoes_highs": referencia.iteracoes,
                "tempo_proprio_ms_mediana": tempo_proprio_ms,
                "tempo_highs_ms_mediana": tempo_highs_ms,
                "aprovado": comparacao.aprovado,
            })

            print(
                f"{problema.id}: {proprio.status}/{referencia.status} "
                f"| aprovado={comparacao.aprovado} "
                f"| erroZ={comparacao.erro_z_relativo}"
            )

    caminho_csv = PASTA_RESULTADOS / "resultados.csv"
    with caminho_csv.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=linhas[0].keys())
        escritor.writeheader()
        escritor.writerows(linhas)

    ambiente = {
        "python": platform.python_version(),
        "plataforma": platform.platform(),
        "processador": platform.processor(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "numero_instancias": len(linhas),
        "seed_base": 3471,
        "repeticoes_tempo": 3,
    }
    (PASTA_RESULTADOS / "ambiente.json").write_text(
        json.dumps(ambiente, indent=2), encoding="utf-8"
    )

    total_aprovado = sum(bool(linha["aprovado"]) for linha in linhas)
    print(f"\nAprovados: {total_aprovado}/{len(linhas)}")
    print(f"CSV: {caminho_csv}")

    if total_aprovado != len(linhas):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
