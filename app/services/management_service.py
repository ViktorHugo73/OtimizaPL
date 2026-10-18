from copy import deepcopy
from sqlalchemy import select
from app.db_models import Problem, Scenario, Execution


def get_locked(db, model, identifier):
    item = db.scalars(select(model).where(model.id == identifier).with_for_update()).first()
    if item is None:
        raise LookupError('Registro não encontrado.')
    return item


def update_metadata(db, model, identifier, data):
    item = get_locked(db, model, identifier)
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(item, name, value)
    db.commit()
    db.refresh(item)
    return item


def delete_permanently(db, model, identifier):
    """Delete executions and their results before the parent, in one transaction."""
    item = get_locked(db, model, identifier)
    column = Execution.problem_id if model is Problem else Execution.scenario_id
    try:
        for execution in db.scalars(select(Execution).where(column == identifier)).all():
            db.delete(execution)
        db.flush()
        db.delete(item)
        db.commit()
    except Exception:
        db.rollback()
        raise


def duplicate_scenario(db, identifier, data):
    source = get_locked(db, Scenario, identifier)
    duplicate = Scenario(problem_id=source.problem_id, name=data.name,
                         description=data.description,
                         model_snapshot=deepcopy(source.model_snapshot))
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    return duplicate
