from datetime import datetime

from pydantic import BaseModel


class VariableResult(BaseModel):
    variable_id: int
    variable_name: str
    value: float


class SolveResponse(BaseModel):
    execution_id: int
    problem_id: int
    status: str
    objective_value: float | None
    iterations_phase1: int
    iterations_phase2: int
    duration_ms: float
    solver_version: str

    variables: list[VariableResult]


class RecordedVariable(BaseModel):
    name: str
    value: float


class ExecutionHistoryItem(BaseModel):
    problem_name: str | None = None
    objective_type: str | None = None
    snapshot_available: bool = False
    recorded_variables: list[RecordedVariable] | None = None
    execution_id: int
    problem_id: int
    status: str
    objective_value: float | None

    iterations_phase1: int
    iterations_phase2: int

    duration_ms: float
    solver_version: str

    created_at: datetime

    variables: list[VariableResult]