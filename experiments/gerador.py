from dataclasses import asdict, dataclass
from typing import List

import numpy as np


@dataclass
class ProblemaGerado:
    id: str
    classe: str
    A: list
    b: list
    c: list
    operadores: list
    objetivo: str
    seed: int
    n_variaveis: int
    n_restricoes: int

    def para_dict(self):
        return asdict(self)


# ============================================================
# 1. FACTÍVEL E LIMITADO
# ============================================================

def gerar_factivel_limitado(
    identificador: str,
    n_variaveis: int,
    n_restricoes_aleatorias: int,
    seed: int,
    objetivo: str,
):

    rng = np.random.default_rng(seed)

    # Ponto garantidamente factível.
    x0 = rng.uniform(
        0.5,
        5.0,
        size=n_variaveis
    )

    A_aleatoria = rng.uniform(
        -3.0,
        5.0,
        size=(
            n_restricoes_aleatorias,
            n_variaveis
        )
    )

    folgas = rng.uniform(
        0.5,
        5.0,
        size=n_restricoes_aleatorias
    )

    # Garante:
    #
    # A*x0 <= b
    #
    b_aleatorio = (
        A_aleatoria @ x0
        +
        folgas
    )

    # Limites superiores garantem que o problema seja limitado.
    limites_superiores = (
        x0
        +
        rng.uniform(
            1.0,
            6.0,
            size=n_variaveis
        )
    )

    A_limites = np.eye(n_variaveis)

    A = np.vstack(
        [
            A_aleatoria,
            A_limites
        ]
    )

    b = np.concatenate(
        [
            b_aleatorio,
            limites_superiores
        ]
    )

    c = rng.uniform(
        -10.0,
        10.0,
        size=n_variaveis
    )

    operadores = (
        ["<="] * len(b)
    )

    return ProblemaGerado(
        id=identificador,
        classe="factivel_limitado",
        A=A.tolist(),
        b=b.tolist(),
        c=c.tolist(),
        operadores=operadores,
        objetivo=objetivo,
        seed=seed,
        n_variaveis=n_variaveis,
        n_restricoes=len(b),
    )


# ============================================================
# 2. FACTÍVEL COM <=, >= E =
# ============================================================

def gerar_factivel_misto(
    identificador: str,
    n_variaveis: int,
    n_restricoes_aleatorias: int,
    seed: int,
    objetivo: str,
):

    rng = np.random.default_rng(seed)

    x0 = rng.uniform(
        0.5,
        5.0,
        size=n_variaveis
    )

    A = []
    b = []
    operadores = []

    tipos = ["<=", ">=", "="]

    for i in range(n_restricoes_aleatorias):

        linha = rng.uniform(
            -3.0,
            5.0,
            size=n_variaveis
        )

        valor_no_x0 = float(
            linha @ x0
        )

        operador = tipos[
            i % len(tipos)
        ]

        if operador == "<=":

            limite = (
                valor_no_x0
                +
                rng.uniform(0.5, 4.0)
            )

        elif operador == ">=":

            limite = (
                valor_no_x0
                -
                rng.uniform(0.5, 4.0)
            )

        else:

            # x0 satisfaz exatamente a igualdade.
            limite = valor_no_x0

        A.append(
            linha.tolist()
        )

        b.append(
            float(limite)
        )

        operadores.append(
            operador
        )

    # Limites superiores:
    #
    # x_j <= U_j
    #
    # tornam a região limitada.

    limites_superiores = (
        x0
        +
        rng.uniform(
            1.0,
            5.0,
            size=n_variaveis
        )
    )

    for j in range(n_variaveis):

        linha = np.zeros(
            n_variaveis
        )

        linha[j] = 1.0

        A.append(
            linha.tolist()
        )

        b.append(
            float(
                limites_superiores[j]
            )
        )

        operadores.append(
            "<="
        )

    c = rng.uniform(
        -10.0,
        10.0,
        size=n_variaveis
    )

    return ProblemaGerado(
        id=identificador,
        classe="factivel_misto",
        A=A,
        b=b,
        c=c.tolist(),
        operadores=operadores,
        objetivo=objetivo,
        seed=seed,
        n_variaveis=n_variaveis,
        n_restricoes=len(b),
    )


# ============================================================
# 3. INVIÁVEL POR CONSTRUÇÃO
# ============================================================

def gerar_inviavel(
    identificador: str,
    n_variaveis: int,
    seed: int,
):

    rng = np.random.default_rng(seed)

    c = rng.uniform(
        -5.0,
        5.0,
        size=n_variaveis
    )

    A = []
    b = []
    operadores = []

    # x1 <= 5

    linha = np.zeros(
        n_variaveis
    )

    linha[0] = 1.0

    A.append(
        linha.tolist()
    )

    b.append(5.0)

    operadores.append("<=")

    # x1 >= 10
    #
    # Contradição proposital.

    linha = np.zeros(
        n_variaveis
    )

    linha[0] = 1.0

    A.append(
        linha.tolist()
    )

    b.append(10.0)

    operadores.append(">=")

    # Limites nas outras variáveis.

    for j in range(1, n_variaveis):

        linha = np.zeros(
            n_variaveis
        )

        linha[j] = 1.0

        A.append(
            linha.tolist()
        )

        b.append(
            float(
                rng.uniform(5.0, 20.0)
            )
        )

        operadores.append("<=")

    return ProblemaGerado(
        id=identificador,
        classe="inviavel",
        A=A,
        b=b,
        c=c.tolist(),
        operadores=operadores,
        objetivo="min",
        seed=seed,
        n_variaveis=n_variaveis,
        n_restricoes=len(b),
    )


# ============================================================
# 4. ILIMITADO POR CONSTRUÇÃO
# ============================================================

def gerar_ilimitado(
    identificador: str,
    n_variaveis: int,
    seed: int,
):

    rng = np.random.default_rng(seed)

    # Maximizar x1.
    #
    # Nenhuma restrição imporá limite superior sobre x1.

    c = np.zeros(
        n_variaveis
    )

    c[0] = 1.0

    A = []
    b = []
    operadores = []

    # Restringe apenas x2...xn.

    for j in range(1, n_variaveis):

        linha = np.zeros(
            n_variaveis
        )

        linha[j] = 1.0

        A.append(
            linha.tolist()
        )

        b.append(
            float(
                rng.uniform(5.0, 20.0)
            )
        )

        operadores.append("<=")

    return ProblemaGerado(
        id=identificador,
        classe="ilimitado",
        A=A,
        b=b,
        c=c.tolist(),
        operadores=operadores,
        objetivo="max",
        seed=seed,
        n_variaveis=n_variaveis,
        n_restricoes=len(b),
    )


# ============================================================
# 5. MÚLTIPLOS ÓTIMOS
# ============================================================

def problema_multiplos_otimos():

    return ProblemaGerado(
        id="MULTI_001",
        classe="multiplos_otimos",

        A=[
            [1.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
        ],

        b=[
            10.0,
            10.0,
            10.0,
        ],

        c=[
            1.0,
            1.0,
        ],

        operadores=[
            "<=",
            "<=",
            "<=",
        ],

        objetivo="max",

        seed=0,

        n_variaveis=2,

        n_restricoes=3,
    )