"""Comparação padronizada entre o Simplex próprio e o HiGHS."""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from .factibilidade import avaliar_factibilidade


@dataclass
class Comparacao:
    status_igual: bool
    erro_z_absoluto: Optional[float]
    erro_z_relativo: Optional[float]
    erro_x_maximo: Optional[float]
    solucao_propria_factivel: Optional[bool]
    violacao_maxima: Optional[float]
    aprovado: bool


def comparar_resultados(
    proprio,
    referencia,
    A,
    b,
    operadores,
    tolerancia_z=1e-7,
    tolerancia_factibilidade=1e-7,
):
    status_igual = proprio.status == referencia.status

    if proprio.status != "optimal" or referencia.status != "optimal":
        return Comparacao(
            status_igual=status_igual,
            erro_z_absoluto=None,
            erro_z_relativo=None,
            erro_x_maximo=None,
            solucao_propria_factivel=None,
            violacao_maxima=None,
            aprovado=status_igual,
        )

    erro_z_abs = abs(proprio.valor_objetivo - referencia.valor_objetivo)
    denominador = max(1.0, abs(referencia.valor_objetivo))
    erro_z_rel = erro_z_abs / denominador

    # Informação diagnóstica; NÃO é critério universal de reprovação porque
    # problemas com múltiplos ótimos podem gerar vetores x diferentes.
    erro_x = float(np.max(np.abs(proprio.x - referencia.x)))

    fact = avaliar_factibilidade(
        A, b, operadores, proprio.x, tolerancia=tolerancia_factibilidade
    )

    aprovado = (
        status_igual
        and erro_z_rel <= tolerancia_z
        and fact.factivel
    )

    return Comparacao(
        status_igual=status_igual,
        erro_z_absoluto=erro_z_abs,
        erro_z_relativo=erro_z_rel,
        erro_x_maximo=erro_x,
        solucao_propria_factivel=fact.factivel,
        violacao_maxima=fact.violacao_maxima,
        aprovado=aprovado,
    )
