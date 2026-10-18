from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import Execution


def get_execution(db: Session, execution_id: int):
    return db.get(Execution, execution_id)


def get_latest_scenario_execution(db: Session, scenario_id: int):
    return db.scalars(
        select(Execution).where(Execution.scenario_id == scenario_id)
        .order_by(Execution.created_at.desc(), Execution.id.desc()).limit(1)
    ).first()
