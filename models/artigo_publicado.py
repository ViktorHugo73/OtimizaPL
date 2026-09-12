"""Transcrição literal das equações numéricas publicadas no artigo.

ATENÇÃO: este NÃO é o modelo corrigido v1.0. Ele existe para registrar e testar
reprodutivelmente a inconsistência da formulação publicada.
"""

MODELO_ARTIGO_PUBLICADO = {
    "nome": "Oficina de feixes - transcrição literal publicada",
    "objetivo": "min",
    "variaveis": ["XR", "XS"],
    "c": [450.0, 800.0],
    "A": [
        [1.0, 1.0],       # demanda
        [1.0, 0.15],      # horas, conforme equação publicada
        [2.0, 10.0],      # mão de obra, conforme equação publicada
        [7.0, -3.0],      # mínimo de reformas
        [1.0, 0.0],       # forno
    ],
    "b": [20.0, 120.0, 60.0, 0.0, 8.0],
    "operadores": [">=", "<=", "<=", ">=", "<="],
}

SOLUCAO_DECLARADA_NO_ARTIGO = {
    "x": [8.0, 12.0],
    "z": 13200.0,
}
