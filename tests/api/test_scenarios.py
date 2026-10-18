from tests.api.payloads import (
    ARTIGO_V1_PAYLOAD
)


def criar_problem(
    client
):

    response = client.post(
        "/api/v1/problems",
        json=ARTIGO_V1_PAYLOAD,
    )

    assert (
        response.status_code
        ==
        201
    )

    return response.json()

def test_criar_e_resolver_cenario_base(
    client
):

    problem = criar_problem(
        client
    )

    problem_id = problem["id"]

    response = client.post(

        f"/api/v1/problems/"
        f"{problem_id}/scenarios",

        json={
            "name":
                "Cenário Base",

            "description":
                "Modelo original.",

            "variable_overrides":
                [],

            "constraint_overrides":
                [],
        }
    )

    assert (
        response.status_code
        ==
        201
    )

    scenario = response.json()

    scenario_id = (
        scenario["id"]
    )

    response = client.post(

        f"/api/v1/scenarios/"
        f"{scenario_id}/solve"
    )

    assert (
        response.status_code
        ==
        200
    )

    result = response.json()

    assert (
        result["status"]
        ==
        "optimal"
    )

    assert abs(

        result["objective_value"]
        -
        13200

    ) <= 1e-7

    variables = {

        item["variable_name"]:
            item["value"]

        for item
        in result["variables"]
    }

    assert abs(
        variables["XR"] - 8
    ) <= 1e-7

    assert abs(
        variables["XS"] - 12
    ) <= 1e-7

def test_scenario_nao_altera_problem_base(
    client
):

    problem = criar_problem(
        client
    )

    problem_id = problem["id"]

    # Cenário altera forno para 10.

    response = client.post(

        f"/api/v1/problems/"
        f"{problem_id}/scenarios",

        json={
            "name":
                "Forno aumentado",

            "constraint_overrides": [
                {
                    "constraint_name":
                        "Capacidade do forno",

                    "rhs":
                        10,
                }
            ],
        }
    )

    assert (
        response.status_code
        ==
        201
    )

    # Consulta problema original.

    response = client.get(

        f"/api/v1/problems/"
        f"{problem_id}"
    )

    original = response.json()

    forno = next(

        item

        for item
        in original["constraints"]

        if item["name"]
        ==
        "Capacidade do forno"
    )

    # O problema original continua em 8.

    assert (
        forno["rhs"]
        ==
        8
    )
    

    
