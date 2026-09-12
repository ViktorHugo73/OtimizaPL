"""Execução e medição dos dois solvers sobre o mesmo problema."""

from dataclasses import dataclass
from statistics import median
from time import perf_counter

from motor import SimplexDuasFases
from motor.simplex import ResultadoPL
from .highs import resolver_highs, ResultadoReferencia
from .comparador import comparar_resultados, Comparacao


@dataclass
class ResultadoBenchmark:
    proprio: ResultadoPL
    referencia: ResultadoReferencia
    comparacao: Comparacao
    tempo_proprio_ms: float
    tempo_highs_ms: float


def executar_comparacao(problema, repeticoes=5):
    """Retorna os resultados finais e a mediana dos tempos, em milissegundos.

    Mede somente as chamadas de resolução; não inclui criação do motor nem
    comparação dos resultados. Não realiza aquecimento prévio dos solvers.
    """
    if isinstance(repeticoes, bool) or not isinstance(repeticoes, int) or repeticoes < 1:
        raise ValueError("repeticoes deve ser um inteiro positivo.")

    argumentos = (
        problema.A, problema.b, problema.c,
        problema.operadores, problema.objetivo,
    )
    tempos_proprio = []
    tempos_highs = []
    for _ in range(repeticoes):
        solver = SimplexDuasFases()
        inicio = perf_counter()
        proprio = solver.resolver(*argumentos)
        tempos_proprio.append((perf_counter() - inicio) * 1000.0)

        inicio = perf_counter()
        referencia = resolver_highs(*argumentos)
        tempos_highs.append((perf_counter() - inicio) * 1000.0)

    comparacao = comparar_resultados(
        proprio, referencia, problema.A, problema.b, problema.operadores,
    )
    return ResultadoBenchmark(
        proprio, referencia, comparacao,
        median(tempos_proprio), median(tempos_highs),
    )
