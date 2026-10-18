def normalizar_float(
    valor: float | None,
    casas: int = 10,
) -> float | None:

    if valor is None:
        return None

    valor = float(
        valor
    )

    if abs(valor) < 1e-10:
        return 0.0

    return round(
        valor,
        casas,
    )