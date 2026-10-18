from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import (
    get_db,
)

from app.repositories.problem_repository import (
    get_problem,
)

from app.repositories.scenario_repository import (
    get_scenario,
    list_scenarios,
)

from app.schemas.optimization import (
    SolveResponse,
)

from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioRead,
)

from app.services.optimization_service import (
    resolver_scenario,
)

from app.services.scenario_service import (
    cadastrar_scenario,
)

from app.schemas.scenario import (
    ScenarioComparisonItem,
    ScenarioComparisonResponse,
    ScenarioCreate,
    ScenarioRead,
)

from app.core.numeric import (
    normalizar_float,
)


router = APIRouter(
    tags=["scenarios"]
)


@router.post(
    "/problems/{problem_id}/scenarios",
    response_model=ScenarioRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_scenario(
    problem_id: int,
    data: ScenarioCreate,
    db: Session = Depends(get_db),
):

    try:

        scenario = cadastrar_scenario(
            db,
            problem_id,
            data,
        )

    except LookupError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    return scenario


@router.get(
    "/problems/{problem_id}/scenarios",
    response_model=list[
        ScenarioRead
    ],
)
def consultar_scenarios(
    problem_id: int,
    db: Session = Depends(get_db),
):

    problem = get_problem(
        db,
        problem_id,
    )

    if problem is None:

        raise HTTPException(
            status_code=404,
            detail="Problema não encontrado.",
        )

    return list_scenarios(
        db,
        problem_id,
    )


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioRead,
)
def consultar_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
):

    scenario = get_scenario(
        db,
        scenario_id,
    )

    if scenario is None:

        raise HTTPException(
            status_code=404,
            detail="Cenário não encontrado.",
        )

    return scenario


@router.post(
    "/scenarios/{scenario_id}/solve",
    response_model=SolveResponse,
)
def solucionar_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
):

    scenario = get_scenario(
        db,
        scenario_id,
    )

    if scenario is None:

        raise HTTPException(
            status_code=404,
            detail="Cenário não encontrado.",
        )

    return resolver_scenario(
        db,
        scenario,
    )

@router.get(
    "/problems/{problem_id}/scenarios/compare",
    response_model=ScenarioComparisonResponse,
)
def comparar_scenarios(
    problem_id: int,
    db: Session = Depends(get_db),
):

    problem = get_problem(
        db,
        problem_id,
    )

    if problem is None:

        raise HTTPException(
            status_code=404,
            detail="Problema não encontrado.",
        )

    scenarios = list_scenarios(
        db,
        problem_id,
    )

    items = []

    for scenario in scenarios:

        if not scenario.executions:

            continue

        execution = max(
            scenario.executions,
            key=lambda item:
                item.created_at
        )

        variables = {

    result.variable.name:
        normalizar_float(
            result.value
        )

    for result
    in execution.variable_results
}

        items.append({

            "scenario_id":
                scenario.id,

            "scenario_name":
                scenario.name,

            "execution_id":
                execution.id,

            "status":
                execution.status,

            "objective_value":
                normalizar_float(
                    execution.objective_value
                ),

            "duration_ms":
                round(
                    execution.duration_ms,4
                ),

            "variables":
                variables,
        })

    return {

        "problem_id":
            problem_id,

        "scenarios":
            items,
    }