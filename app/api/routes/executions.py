from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.session import (
    get_db,
)

from app.schemas.resource_analysis import (
    ResourceAnalysisResponse,
)

from app.services.resource_analysis_service import (
    analisar_recursos,
)


router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.get(
    "/{execution_id}/resources",
    response_model=ResourceAnalysisResponse,
)
def consultar_analise_recursos(
    execution_id: int,
    db: Session = Depends(get_db),
):

    try:

        return analisar_recursos(
            db,
            execution_id,
        )


    except LookupError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


    except ValueError as error:

        raise HTTPException(
            status_code=409,
            detail=str(error),
        )