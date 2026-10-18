from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.db_models import Scenario
from app.repositories.resource_analysis_repository import get_execution, get_latest_scenario_execution
from app.schemas.resource_analysis import ResourceAnalysisResponse
from app.services.resource_analysis_service import analyze_execution

router = APIRouter(tags=['Resource analysis'])


def response_for(execution):
    if execution is None:
        raise HTTPException(status_code=404, detail='Execução não encontrada.')
    try:
        return analyze_execution(execution)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get('/executions/{execution_id}/resources', response_model=ResourceAnalysisResponse)
def execution_resources(execution_id: int, db: Session = Depends(get_db)):
    return response_for(get_execution(db, execution_id))


@router.get('/scenarios/{scenario_id}/resources', response_model=ResourceAnalysisResponse)
def scenario_resources(scenario_id: int, db: Session = Depends(get_db)):
    if db.get(Scenario, scenario_id) is None:
        raise HTTPException(status_code=404, detail='Cenário não encontrado.')
    execution = get_latest_scenario_execution(db, scenario_id)
    if execution is None:
        raise HTTPException(status_code=409, detail='Cenário ainda não executado.')
    return response_for(execution)
