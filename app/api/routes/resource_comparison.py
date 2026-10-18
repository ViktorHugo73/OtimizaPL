from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.db_models import Problem, Scenario
from app.repositories.resource_analysis_repository import get_execution, get_latest_scenario_execution
from app.schemas.resource_comparison import ResourceComparisonResponse
from app.services.resource_comparison_service import compare_executions

router = APIRouter(tags=['Resource comparison'])


def select_execution(db, problem_id, scenario_id, execution_id):
    scenario = db.get(Scenario, scenario_id)
    if scenario is None or scenario.problem_id != problem_id:
        raise HTTPException(404, 'Cenário não encontrado neste problema.')
    if execution_id is not None:
        execution = get_execution(db, execution_id)
        if execution is None or execution.scenario_id != scenario_id or execution.problem_id != problem_id:
            raise HTTPException(404, 'Execução não encontrada neste cenário.')
    else:
        execution = get_latest_scenario_execution(db, scenario_id)
        if execution is None:
            raise HTTPException(409, 'Cenário ainda não executado.')
    return execution


@router.get('/problems/{problem_id}/scenarios/compare/resources', response_model=ResourceComparisonResponse)
def compare_resources(
    problem_id: int,
    baseline_scenario_id: int = Query(..., gt=0),
    target_scenario_id: int = Query(..., gt=0),
    baseline_execution_id: int | None = Query(None, gt=0),
    target_execution_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
):
    if db.get(Problem, problem_id) is None:
        raise HTTPException(404, 'Problema não encontrado.')
    baseline = select_execution(db, problem_id, baseline_scenario_id, baseline_execution_id)
    target = select_execution(db, problem_id, target_scenario_id, target_execution_id)
    try:
        return compare_executions(baseline, target)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
