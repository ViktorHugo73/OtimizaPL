from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class VariableOverride(BaseModel):

    variable_name: str

    objective_coefficient: float | None = None

    lower_bound: float | None = None

    upper_bound: float | None = None


class ConstraintOverride(BaseModel):

    constraint_name: str

    rhs: float | None = None

    operator: str | None = None

    coefficients: dict[str, float] | None = None


class ScenarioCreate(BaseModel):

    source_execution_id: int | None = Field(default=None, gt=0)

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    variable_overrides: list[
        VariableOverride
    ] = []

    constraint_overrides: list[
        ConstraintOverride
    ] = []


class ScenarioRead(BaseModel):

    id: int

    problem_id: int

    name: str

    description: str | None

    created_at: datetime

    model_snapshot: dict


class ScenarioComparisonItem(BaseModel):

    scenario_id: int

    scenario_name: str

    execution_id: int

    status: str

    objective_value: float | None

    duration_ms: float

    variables: dict[str, float]


class ScenarioComparisonResponse(BaseModel):

    problem_id: int

    scenarios: list[
        ScenarioComparisonItem
    ]