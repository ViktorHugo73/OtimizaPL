from motor import SimplexDuasFases, verificar_restricoes
from models.artigo_publicado import (
    MODELO_ARTIGO_PUBLICADO,
    SOLUCAO_DECLARADA_NO_ARTIGO,
)
from validacao import resolver_highs


def test_transcricao_literal_publicada_e_inviavel():
    m = MODELO_ARTIGO_PUBLICADO
    solver = SimplexDuasFases()

    proprio = solver.resolver(
        m["A"], m["b"], m["c"], m["operadores"], m["objetivo"]
    )
    referencia = resolver_highs(
        m["A"], m["b"], m["c"], m["operadores"], m["objetivo"]
    )

    assert proprio.status == "infeasible"
    assert referencia.status == "infeasible"


def test_solucao_declarada_8_12_viola_equacao_publicada():
    m = MODELO_ARTIGO_PUBLICADO
    x = SOLUCAO_DECLARADA_NO_ARTIGO["x"]

    checagem = verificar_restricoes(
        m["A"], m["b"], m["operadores"], x
    )

    # A terceira restrição é a de mão de obra: 2*8 + 10*12 <= 60.
    assert checagem[2]["lado_esquerdo"] == 136.0
    assert checagem[2]["lado_direito"] == 60.0
    assert checagem[2]["satisfeita"] is False
