import numpy as np
import pytest
from models.mix_producao import carregar_modelo_mix
from motor import SimplexDuasFases
from validacao import resolver_highs, comparar_resultados


@pytest.mark.parametrize('limits,expected,z', [
    ([4, 12, 18], [2, 6, 0], 36),
    ([4, 12, 24], [4, 6, 0], 42),
    ([4, 15, 18], [1, 7.5, 0], 40.5),
])
def test_mix_against_analytical_optimum_and_highs(limits, expected, z):
    model = carregar_modelo_mix()
    args = (model['A'], limits, model['c'], model['operadores'], model['objetivo'])
    result = SimplexDuasFases().resolver(*args)
    reference = resolver_highs(*args)
    assert comparar_resultados(result, reference, model['A'], limits, model['operadores']).aprovado
    assert result.status == 'optimal'
    np.testing.assert_allclose(result.x, expected, atol=1e-7, rtol=0)
    assert result.valor_objetivo == pytest.approx(z, abs=1e-7)
    # Independent upper bound: montagem + 1.5 * usinagem >= objective.
    assert z == limits[2] + 1.5 * limits[1]


def test_incompatible_minimum_production():
    model = carregar_modelo_mix()
    A = model['A'] + [[1, 0, 0]]
    b = model['b'] + [5]
    operators = model['operadores'] + ['>=']
    own = SimplexDuasFases().resolver(A, b, model['c'], operators, 'max')
    reference = resolver_highs(A, b, model['c'], operators, 'max')
    assert own.status == reference.status == 'infeasible'
