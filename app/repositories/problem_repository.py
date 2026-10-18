from sqlalchemy import select

from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.db_models import (
    Constraint,
    ConstraintCoefficient,
    Problem,
    Variable,
)

from app.db_models import (
    Constraint,
    ConstraintCoefficient,
    Execution,
    Problem,
    ResultVariable,
    Variable,
)

from app.schemas.problem import ProblemCreate


def get_problem(
    db: Session,
    problem_id: int,
):

    statement = (
        select(Problem)
        .where(
            Problem.id == problem_id
        )
        .options(
            selectinload(
                Problem.variables
            ),
            selectinload(
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


def create_problem(
    db: Session,
    data: ProblemCreate,
):

    problem = Problem(
        name=data.name,
        description=data.description,
        objective_type=data.objective_type,
    )

    db.add(problem)

    db.flush()

    variaveis = {}

    for item in data.variables:

        variable = Variable(
            problem_id=problem.id,
            name=item.name,
            description=item.description,
            objective_coefficient=(
                item.objective_coefficient
            ),
            lower_bound=item.lower_bound,
            upper_bound=item.upper_bound,
        )

        db.add(variable)

        db.flush()

        variaveis[
            item.name
        ] = variable

    for item in data.constraints:

        constraint = Constraint(
            problem_id=problem.id,
            name=item.name,
            operator=item.operator,
            rhs=item.rhs,
        )

        db.add(constraint)

        db.flush()

        for term in item.terms:

            variable = variaveis[
                term.variable_name
            ]

            coefficient = ConstraintCoefficient(
                constraint_id=constraint.id,
                variable_id=variable.id,
                coefficient=term.coefficient,
            )

            db.add(coefficient)

    db.commit()

    return get_problem(
        db,
        problem.id,
    )

def list_executions(
    db: Session,
    problem_id: int,
):

    statement = (
        select(Execution)
        .where(
            Execution.problem_id
            ==
            problem_id
        )
        .options(
            selectinload(
                Execution.variable_results
            )
            .selectinload(
                ResultVariable.variable
            )
        )
        .order_by(
            Execution.created_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )