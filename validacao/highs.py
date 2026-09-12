"""Adaptador SciPy/HiGHS usado somente como oráculo de referência."""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy.optimize import linprog


@dataclass
class ResultadoReferencia:
    status: str
    x: Optional[np.ndarray]
    valor_objetivo: Optional[float]
    iteracoes: Optional[int]
    mensagem: str


def resolver_highs(A, b, c, operadores, objetivo="min") -> ResultadoReferencia:
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)

    A_ub, b_ub = [], []
    A_eq, b_eq = [], []

    for linha, limite, operador in zip(A, b, operadores):
        if operador == "<=":
            A_ub.append(linha)
            b_ub.append(limite)
        elif operador == ">=":
            # HiGHS recebe desigualdades no formato A_ub x <= b_ub.
            A_ub.append(-linha)
            b_ub.append(-limite)
        elif operador == "=":
            A_eq.append(linha)
            b_eq.append(limite)
        else:
            raise ValueError(f"Operador inválido: {operador}")

    if objetivo not in ("min", "max"):
        raise ValueError("objetivo deve ser 'min' ou 'max'.")

    c_highs = c if objetivo == "min" else -c

    resultado = linprog(
        c=c_highs,
        A_ub=np.asarray(A_ub, dtype=float) if A_ub else None,
        b_ub=np.asarray(b_ub, dtype=float) if b_ub else None,
        A_eq=np.asarray(A_eq, dtype=float) if A_eq else None,
        b_eq=np.asarray(b_eq, dtype=float) if b_eq else None,
        bounds=[(0.0, None)] * len(c),
        method="highs",
    )

    mapa_status = {
        0: "optimal",
        2: "infeasible",
        3: "unbounded",
    }
    status = mapa_status.get(resultado.status, "other")

    if status == "optimal":
        x = np.asarray(resultado.x, dtype=float)
        z = float(c @ x)  # devolve sempre no sentido original do problema
    else:
        x = None
        z = None

    return ResultadoReferencia(
        status=status,
        x=x,
        valor_objetivo=z,
        iteracoes=getattr(resultado, "nit", None),
        mensagem=str(resultado.message),
    )
