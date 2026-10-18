from typing import Literal
from pydantic import BaseModel


class ConstraintResourceAnalysis(BaseModel):
    name: str
    kind: Literal['constraint', 'lower_bound', 'upper_bound']
    operator: str
    lhs: float
    rhs: float
    residual: float
    violation: float
    tolerance: float
    slack: float | None
    excess: float | None
    distance_to_boundary: float
    utilization_percent: float | None
    is_active: bool
    is_feasible: bool
    potential_bottleneck: bool


class ResourceAnalysisResponse(BaseModel):
    execution_id: int
    problem_id: int
    scenario_id: int | None
    status: str
    objective_value: float | None
    is_feasible: bool
    resources: list[ConstraintResourceAnalysis]
