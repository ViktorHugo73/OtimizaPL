from typing import Literal

from pydantic import BaseModel, ConfigDict
from app.schemas.resource_analysis import ResourceAnalysisResponse, ConstraintResourceAnalysis


class ResourceDifference(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    name: str
    kind: str
    baseline: ConstraintResourceAnalysis | None
    target: ConstraintResourceAnalysis | None
    comparable: bool
    reason: str | None = None
    lhs_delta: float | None = None
    rhs_delta: float | None = None
    slack_delta: float | None = None
    excess_delta: float | None = None
    utilization_delta_pp: float | None = None
    activity_change: Literal['became_active', 'became_inactive', 'unchanged'] | None = None
    bottleneck_change: Literal['became_potential', 'ceased_potential', 'unchanged'] | None = None


class ResourceComparisonResponse(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    problem_id: int
    baseline: ResourceAnalysisResponse
    target: ResourceAnalysisResponse
    objective_comparable: bool
    objective_reason: str | None
    objective_delta: float | None
    objective_delta_percent: float | None
    objective_improvement: float | None
    resources: list[ResourceDifference]
    interpretation: str = (
        'Deltas = cenário comparado menos cenário de referência. Utilização em pontos '
        'percentuais. Melhoria positiva indica redução de custo (min) ou aumento de '
        'resultado (max). Gargalo potencial não comprova impacto marginal.'
    )
