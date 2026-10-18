from tests.api.payloads import (
    ARTIGO_V1_PAYLOAD
)


def test_criar_problem(
    client
):

    response = client.post(

        "/api/v1/problems",

        json=ARTIGO_V1_PAYLOAD
    )

    assert (
        response.status_code
        ==
        201
    )

    data = response.json()

    assert (
        data["name"]
        ==
        "Oficina de feixes - artigo v1.0"
    )

    assert (
        data["objective_type"]
        ==
        "min"
    )

    assert (
        len(
            data["variables"]
        )
        ==
        2
    )

    assert (
        len(
            data["constraints"]
        )
        ==
        6
    )

def test_criar_e_resolver_artigo(
    client
):

    # ========================================================
    # 1. CRIA O PROBLEMA
    # ========================================================

    response = client.post(

        "/api/v1/problems",

        json=ARTIGO_V1_PAYLOAD
    )

    assert (
        response.status_code
        ==
        201
    )

    problem = response.json()

    problem_id = problem[
        "id"
    ]


    # ========================================================
    # 2. EXECUTA O SIMPLEX
    # ========================================================

    response = client.post(

        f"/api/v1/problems/"
        f"{problem_id}/solve"
    )


    assert (
        response.status_code
        ==
        200
    )


    resultado = response.json()


    # ========================================================
    # 3. VALIDA RESULTADO
    # ========================================================

    assert (
        resultado["status"]
        ==
        "optimal"
    )


    assert abs(

        resultado[
            "objective_value"
        ]

        -

        13200.0

    ) <= 1e-7


    variaveis = {

        item[
            "variable_name"
        ]:
        item[
            "value"
        ]

        for item
        in resultado[
            "variables"
        ]
    }


    assert abs(
        variaveis["XR"]
        -
        8.0
    ) <= 1e-7


    assert abs(
        variaveis["XS"]
        -
        12.0
    ) <= 1e-7

def test_historico_execucoes(
    client
):

    # Cria problema.

    response = client.post(

        "/api/v1/problems",

        json=ARTIGO_V1_PAYLOAD
    )

    problem_id = (
        response.json()["id"]
    )


    # Executa 3 vezes.

    for _ in range(3):

        response = client.post(

            f"/api/v1/problems/"
            f"{problem_id}/solve"
        )

        assert (
            response.status_code
            ==
            200
        )


    # Consulta histórico.

    response = client.get(

        f"/api/v1/problems/"
        f"{problem_id}/executions"
    )


    assert (
        response.status_code
        ==
        200
    )


    historico = response.json()


    assert len(
        historico
    ) == 3


    for execution in historico:

        assert (
            execution["status"]
            ==
            "optimal"
        )

        assert abs(

            execution[
                "objective_value"
            ]

            -

            13200.0

        ) <= 1e-7

def test_problem_inexistente(
    client
):

    response = client.get(
        "/api/v1/problems/999999"
    )

    assert (
        response.status_code
        ==
        404
    )


def test_resolver_problem_inexistente(
    client
):

    response = client.post(
        "/api/v1/problems/999999/solve"
    )

    assert (
        response.status_code
        ==
        404
    )

def test_restricao_com_variavel_inexistente(
    client
):

    payload = {

        "name":
            "Teste inválido",

        "objective_type":
            "min",

        "variables": [

            {
                "name":
                    "X1",

                "objective_coefficient":
                    1,

                "lower_bound":
                    0
            }
        ],

        "constraints": [

            {
                "name":
                    "Restrição inválida",

                "operator":
                    "<=",

                "rhs":
                    10,

                "terms": [

                    {
                        "variable_name":
                            "X2",

                        "coefficient":
                            1
                    }
                ]
            }
        ]
    }


    response = client.post(

        "/api/v1/problems",

        json=payload
    )


    assert (
        response.status_code
        ==
        422
    )