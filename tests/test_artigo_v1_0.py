import numpy as np
import pytest

from motor import SimplexDuasFases
from models import artigo_v1_0
from validacao import resolver_highs, comparar_resultados


@pytest.mark.skipif(
    not artigo_v1_0.MODELO_FECHADO,
    reason="Modelo artigo_v1.0 ainda não auditado/fechado.",
)
def test_artigo_v1_0_definitivo():
    m = artigo_v1_0.carregar_modelo_artigo_v1_0()
    esperado = artigo_v1_0.SOLUCAO_ESPERADA

    assert esperado["x"] is not None
    assert esperado["z"] is not None

    solver = SimplexDuasFases()

    proprio = solver.resolver(
        m["A"], m["b"], m["c"], m["operadores"], m["objetivo"]
    )
    referencia = resolver_highs(
        m["A"], m["b"], m["c"], m["operadores"], m["objetivo"]
    )

    comparacao = comparar_resultados(
        proprio, referencia, m["A"], m["b"], m["operadores"]
    )

    assert comparacao.aprovado
    assert proprio.status == "optimal"
    assert np.allclose(proprio.x, esperado["x"], atol=1e-7)
    assert np.isclose(proprio.valor_objetivo, esperado["z"], atol=1e-7)
