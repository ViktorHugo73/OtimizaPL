def test_health(
    client
):

    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        ==
        "ok"
    )

    assert (
        data["motor_version"]
        ==
        "1.0.0"
    )

    assert (
        data["motor_status"]
        ==
        "validated"
    )