import numpy as np

from motor import SimplexDuasFases
from validacao import resolver_highs, comparar_resultados


solver = SimplexDuasFases()


def validar_com_highs(A, b, c, operadores, objetivo):
    proprio = solver.resolver(A, b, c, operadores, objetivo)
    referencia = resolver_highs(A, b, c, operadores, objetivo)
    comparacao = comparar_resultados(
        proprio, referencia, A, b, operadores
    )
    assert comparacao.aprovado, (proprio, referencia, comparacao)
    return proprio, referencia


def test_maximizacao_simples():
    A = [[1, 1], [1, 0], [0, 1]]
    b = [4, 2, 3]
    c = [3, 2]
    ops = ["<=", "<=", "<="]

    proprio, _ = validar_com_highs(A, b, c, ops, "max")

    assert np.allclose(proprio.x, [2, 2], atol=1e-7)
    assert np.isclose(proprio.valor_objetivo, 10.0, atol=1e-7)


def test_minimizacao_com_maior_igual():
    A = [[1, 1], [1, 3]]
    b = [4, 6]
    c = [2, 3]
    ops = [">=", ">="]

    proprio, _ = validar_com_highs(A, b, c, ops, "min")

    assert np.allclose(proprio.x, [3, 1], atol=1e-7)
    assert np.isclose(proprio.valor_objetivo, 9.0, atol=1e-7)


def test_restricao_de_igualdade():
    A = [[1, 1], [1, 0]]
    b = [3, 2]
    c = [1, 1]
    ops = ["=", "<="]

    proprio, referencia = validar_com_highs(A, b, c, ops, "max")

    assert np.isclose(proprio.valor_objetivo, 3.0, atol=1e-7)
    assert np.isclose(referencia.valor_objetivo, 3.0, atol=1e-7)


def test_modelo_inviavel():
    A = [[1], [1]]
    b = [2, 1]
    c = [1]
    ops = [">=", "<="]

    proprio, referencia = validar_com_highs(A, b, c, ops, "min")
    assert proprio.status == "infeasible"
    assert referencia.status == "infeasible"


def test_modelo_ilimitado():
    A = [[1]]
    b = [1]
    c = [1]
    ops = [">="]

    proprio, referencia = validar_com_highs(A, b, c, ops, "max")
    assert proprio.status == "unbounded"
    assert referencia.status == "unbounded"
