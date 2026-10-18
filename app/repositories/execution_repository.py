from sqlalchemy import select

from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.db_models import (
    Constraint,
    ConstraintCoefficient,
    Execution,
    Problem,
    ResultVariable,
)


def get_execution_for_analysis(
    db: Session,
    execution_id: int,
):

    statement = (
        select(Execution)
        .where(
            Execution.id
            ==
            execution_id
        )
        .options(

            # Resultado das variáveis

            selectinload(
                Execution.variable_results
            )
            .selectinload(
                ResultVariable.variable
            ),

            # Cenário, caso exista

            selectinload(
                Execution.scenario
            ),

            # Problema-base

            selectinload(
                Execution.problem
            )
            .selectinload(
                Problem.variables
            ),

            selectinload(
                Execution.problem
            )
            .selectinload(
                Problem.constraints
            )
            .selectinload(
                Constraint.coefficients
            )
            .selectinload(
                ConstraintCoefficient.variable
            ),
        )
    )

    return db.scalars(
        statement
    ).first()