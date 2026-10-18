from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.optimization import (
    ExecutionHistoryItem,
    SolveResponse,
)

from app.schemas.problem import (
    ProblemCreate,
    ProblemRead,
)

from app.services.optimization_service import (
    resolver_problem,
    serializar_execution,
)

from app.services.problem_service import (
    cadastrar_problem,
    serializar_problem,
)

from app.repositories.problem_repository import (
    get_problem,
    list_executions,
)


router = APIRouter(
    prefix="/problems",
    tags=["problems"],
)


@router.post(
    "",
    response_model=ProblemRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_problem(
    data: ProblemCreate,
    db: Session = Depends(get_db),
):

    try:

        problem = cadastrar_problem(
            db,
            data,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    return serializar_problem(
        problem
    )


@router.get(
    "/{problem_id}",
    response_model=ProblemRead,
)
def consultar_problem(
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

    return serializar_problem(
        problem
    )


@router.post(
    "/{problem_id}/solve",
    response_model=SolveResponse,
)
def solucionar_problem(
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

    return resolver_problem(
        db,
        problem,
    )

@router.get(
    "/{problem_id}/executions",
    response_model=list[
        ExecutionHistoryItem
    ],
)
def consultar_historico(
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

    executions = list_executions(
        db,
        problem_id,
    )

    return [
        serializar_execution(
            execution
        )

        for execution
        in executions
    ]