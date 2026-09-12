"""Modelo reconstruído adotado para validação computacional do TCC.

Formulação fornecida e adotada pelo usuário. TR, TS, MR e MS são inferidos;
a coincidência com os resultados não comprova os coeficientes originais.
MODELO_FECHADO indica parâmetros definidos, não auditoria da fonte original.
Não constitui declaração de versão estável do motor.
"""

MODELO_FECHADO = True
COEFICIENTES_ORIGINAIS_CONFIRMADOS = False

CR = 450.0
CS = 800.0
D = 20.0
ALPHA = 0.30
TF = 2.0
FMAX = 16.0

# Coeficientes reconstruídos por inferência, adotados explicitamente.
TR = 3.0
TS = 1.5
H = 80.0
MR = 2.0
MS = 1.0
L = 40.0
XS_MAX = 25.0

SOLUCAO_ESPERADA = {"x": [8.0, 12.0], "z": 13200.0}


def carregar_modelo_artigo_v1_0():
    if not MODELO_FECHADO:
        raise RuntimeError("O modelo reconstruído artigo_v1.0 ainda não foi fechado.")

    parametros = [TR, TS, H, MR, MS, L, XS_MAX]
    if any(valor is None for valor in parametros):
        raise RuntimeError("Há parâmetros não preenchidos no modelo artigo_v1.0.")

    return {
        "nome": "Oficina de feixes - artigo v1.0 reconstruído (coeficientes inferidos)",
        "objetivo": "min",
        "variaveis": ["XR", "XS"],
        "c": [CR, CS],
        # XR e XS >= 0 são impostos pelos dois solvers.
        "A": [
            [1.0, 1.0],                  # demanda
            [TR, TS],                    # horas
            [MR, MS],                    # mão de obra
            [0.0, 1.0],                  # limite de XS
            [1.0 - ALPHA, -ALPHA],       # equivalente a 7 XR - 3 XS >= 0
            [TF, 0.0],                   # equivalente a XR <= 8
        ],
        "b": [D, H, L, XS_MAX, 0.0, FMAX],
        "operadores": [">=", "<=", "<=", "<=", ">=", "<="],
    }
