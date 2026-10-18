from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.db_models import Problem, Scenario
from app.schemas.management import MetadataPatch, MetadataUpdate, ProblemSummary
from app.schemas.scenario import ScenarioRead
from app.services.management_service import update_metadata, delete_permanently, duplicate_scenario

router = APIRouter(tags=['Management'])


def perform(db, action, *args):
    try:
        return action(db, *args)
    except LookupError as exc:
        db.rollback()
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from exc


@router.get('/problems', response_model=list[ProblemSummary])
def list_problems(db: Session = Depends(get_db)):
    return list(db.scalars(select(Problem).order_by(Problem.created_at.desc(), Problem.id.desc())).all())


@router.patch('/problems/{problem_id}', response_model=ProblemSummary)
def edit_problem(problem_id: int, data: MetadataPatch, db: Session = Depends(get_db)):
    return perform(db, update_metadata, Problem, problem_id, data)


@router.patch('/scenarios/{scenario_id}', response_model=ScenarioRead)
def edit_scenario(scenario_id: int, data: MetadataPatch, db: Session = Depends(get_db)):
    return perform(db, update_metadata, Scenario, scenario_id, data)


@router.delete('/problems/{problem_id}', status_code=204)
def remove_problem(problem_id: int, confirm: bool = Query(False), db: Session = Depends(get_db)):
    if not confirm:
        raise HTTPException(400, 'Confirme a exclusão com confirm=true.')
    perform(db, delete_permanently, Problem, problem_id)
    return Response(status_code=204)


@router.delete('/scenarios/{scenario_id}', status_code=204)
def remove_scenario(scenario_id: int, confirm: bool = Query(False), db: Session = Depends(get_db)):
    if not confirm:
        raise HTTPException(400, 'Confirme a exclusão com confirm=true.')
    perform(db, delete_permanently, Scenario, scenario_id)
    return Response(status_code=204)


@router.post('/scenarios/{scenario_id}/duplicate', response_model=ScenarioRead, status_code=201)
def copy_scenario(scenario_id: int, data: MetadataUpdate, db: Session = Depends(get_db)):
    return perform(db, duplicate_scenario, scenario_id, data)
