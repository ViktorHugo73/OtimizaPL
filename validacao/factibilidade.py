"""Verificação independente da factibilidade de uma solução."""

from dataclasses import dataclass
import numpy as np


@dataclass
class RelatorioFactibilidade:
    factivel: bool
    violacao_maxima: float
    violacao_nao_negatividade: float


def avaliar_factibilidade(A, b, operadores, x, tolerancia=1e-7):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    x = np.asarray(x, dtype=float)

    lhs = A @ x
    violacoes = []

    for valor, limite, operador in zip(lhs, b, operadores):
        if operador == "<=":
            violacao = max(0.0, float(valor - limite))
        elif operador == ">=":
            violacao = max(0.0, float(limite - valor))
        elif operador == "=":
            violacao = abs(float(valor - limite))
        else:
            raise ValueError(f"Operador inválido: {operador}")
        violacoes.append(violacao)

    violacao_nao_negatividade = max(0.0, float(-np.min(x))) if len(x) else 0.0
    violacao_maxima = max(violacoes + [violacao_nao_negatividade], default=0.0)

    return RelatorioFactibilidade(
        factivel=violacao_maxima <= tolerancia,
        violacao_maxima=violacao_maxima,
        violacao_nao_negatividade=violacao_nao_negatividade,
    )
