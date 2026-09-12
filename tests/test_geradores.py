import pytest

from motor import SimplexDuasFases

from experiments.gerador import (
    gerar_factivel_limitado,
    gerar_factivel_misto,
    gerar_inviavel,
    gerar_ilimitado,
)

from validacao import (
    resolver_highs,
    comparar_resultados
)


solver = SimplexDuasFases()


@pytest.mark.parametrize(
    "seed",
    range(10)
)
def test_factibilidade_limitada(seed):

    problema = gerar_factivel_limitado(

        identificador=f"T_FL_{seed}",

        n_variaveis=5,

        n_restricoes_aleatorias=8,

        seed=seed,

        objetivo=(
            "min"
            if seed % 2 == 0
            else "max"
        )
    )

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

    comparacao = comparar_resultados(

        proprio,

        referencia,

        problema.A,

        problema.b,

        problema.operadores
    )

    assert comparacao.aprovado


@pytest.mark.parametrize(
    "seed",
    range(10)
)
def test_factibilidade_mista(seed):

    problema = gerar_factivel_misto(

        identificador=f"T_FM_{seed}",

        n_variaveis=4,

        n_restricoes_aleatorias=6,

        seed=1000 + seed,

        objetivo=(
            "min"
            if seed % 2 == 0
            else "max"
        )
    )

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

    comparacao = comparar_resultados(

        proprio,

        referencia,

        problema.A,

        problema.b,

        problema.operadores
    )

    assert comparacao.aprovado


@pytest.mark.parametrize(
    "seed",
    range(10)
)
def test_inviaveis(seed):

    problema = gerar_inviavel(

        identificador=f"T_INV_{seed}",

        n_variaveis=5,

        seed=2000 + seed
    )

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

    assert proprio.status == "infeasible"

    assert referencia.status == "infeasible"


@pytest.mark.parametrize(
    "seed",
    range(10)
)
def test_ilimitados(seed):

    problema = gerar_ilimitado(

        identificador=f"T_UNB_{seed}",

        n_variaveis=5,

        seed=3000 + seed
    )

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

    assert proprio.status == "unbounded"

    assert referencia.status == "unbounded"