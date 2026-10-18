from sqlalchemy import select

from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.db_models import (
    Problem,
    Scenario,
)


def create_scenario(
    db: Session,
    problem_id: int,
    name: str,
    description: str | None,
    model_snapshot: dict,
):

    scenario = Scenario(
        problem_id=problem_id,
        name=name,
        description=description,
        model_snapshot=model_snapshot,
    )

    db.add(
        scenario
    )

    db.commit()

    db.refresh(
        scenario
    )

    return scenario


def get_scenario(
    db: Session,
    scenario_id: int,
):

    statement = (
        select(Scenario)
        .where(
            Scenario.id
            ==
            scenario_id
        )
        .options(
            selectinload(
                Scenario.problem
            )
            .selectinload(
                Problem.variables
            )
        )
    )

    return db.scalars(
        statement
    ).first()


def list_scenarios(
    db: Session,
    problem_id: int,
):

    statement = (
        select(Scenario)
        .where(
            Scenario.problem_id == problem_id
        )
        .order_by(
            Scenario.created_at.asc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )