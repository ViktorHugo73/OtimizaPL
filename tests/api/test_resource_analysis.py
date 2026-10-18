import pytest

from tests.api.payloads import (
    ARTIGO_V1_PAYLOAD,
)


def test_analise_recursos_artigo(
    client,
):

    # ========================================================
    # CRIA PROBLEMA
    # ========================================================

    response = client.post(
        "/api/v1/problems",
        json=ARTIGO_V1_PAYLOAD,
    )

    assert (
        response.status_code
        ==
        201
    )

    problem_id = (
        response.json()["id"]
    )


    # ========================================================
    # CRIA CENÁRIO BASE
    # ========================================================

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
        },
    )

    assert (
        response.status_code
        ==
        201
    )


    scenario_id = (
        response.json()["id"]
    )


    # ========================================================
    # RESOLVE
    # ========================================================

    response = client.post(

        f"/api/v1/scenarios/"
        f"{scenario_id}/solve"
    )

    assert (
        response.status_code
        ==
        200
    )


    execution_id = (
        response.json()[
            "execution_id"
        ]
    )


    # ========================================================
    # ANALISA RECURSOS
    # ========================================================

    response = client.get(

        f"/api/v1/executions/"
        f"{execution_id}/resources"
    )

    assert (
        response.status_code
        ==
        200
    )


    data = response.json()


    assert (
        data["objective_value"]
        ==
        pytest.approx(13200.0, abs=1e-7)
    )


    resources = {

        item["name"]:
            item

        for item
        in data[
            "resources"
        ]
    }


    # ========================================================
    # HORAS
    # ========================================================

    horas = resources[
        "Horas"
    ]

    assert horas["lhs"] == pytest.approx(42.0, abs=1e-7)

    assert horas["rhs"] == pytest.approx(80.0, abs=1e-7)

    assert horas["slack"] == pytest.approx(38.0, abs=1e-7)

    assert (
        horas[
            "utilization_percent"
        ]
        ==
        pytest.approx(52.5, abs=1e-7)
    )

    assert (
        horas["is_active"]
        is False
    )


    # ========================================================
    # MÃO DE OBRA
    # ========================================================

    mao_obra = resources[
        "Mão de obra"
    ]

    assert (
        mao_obra["lhs"]
        ==
        pytest.approx(28.0, abs=1e-7)
    )

    assert (
        mao_obra["slack"]
        ==
        pytest.approx(12.0, abs=1e-7)
    )

    assert (
        mao_obra[
            "utilization_percent"
        ]
        ==
        pytest.approx(70.0, abs=1e-7)
    )


    # ========================================================
    # FORNO
    # ========================================================

    forno = resources[
        "Capacidade do forno"
    ]

    assert forno["lhs"] == pytest.approx(8.0, abs=1e-7)

    assert forno["rhs"] == pytest.approx(8.0, abs=1e-7)

    assert forno["slack"] == pytest.approx(0.0, abs=1e-7)

    assert (
        forno[
            "utilization_percent"
        ]
        ==
        pytest.approx(100.0, abs=1e-7)
    )

    assert (
        forno["is_active"]
        is True
    )

    assert (
        forno[
            "potential_bottleneck"
        ]
        is True
    )