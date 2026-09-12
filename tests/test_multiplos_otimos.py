import numpy as np

from motor import SimplexDuasFases

from experiments.gerador import (
    problema_multiplos_otimos
)

from validacao import (
    resolver_highs,
    avaliar_factibilidade
)


def test_multiplos_otimos():

    problema = (
        problema_multiplos_otimos()
    )

    solver = SimplexDuasFases()

    proprio = solver.resolver(

        problema.A,

        problema.b,

        problema.c,

        problema.operadores,

        problema.objetivo
    )

    referencia = resolver_highs(

        problema.A,

        problema.b,

        problema.c,

        problema.operadores,

        problema.objetivo
    )

    assert proprio.status == "optimal"

    assert referencia.status == "optimal"

    # O valor ótimo deve ser o mesmo.

    assert np.isclose(

        proprio.valor_objetivo,

        10.0,

        atol=1e-7
    )

    assert np.isclose(

        referencia.valor_objetivo,

        10.0,

        atol=1e-7
    )

    # A solução do motor deve ser factível.

    factibilidade = avaliar_factibilidade(

        problema.A,

        problema.b,

        problema.operadores,

        proprio.x
    )

    assert factibilidade.factivel

    # NÃO fazemos:
    #
    # assert proprio.x == referencia.x
    #
    # pois há infinitas soluções ótimas:
    #
    # x1 + x2 = 10.