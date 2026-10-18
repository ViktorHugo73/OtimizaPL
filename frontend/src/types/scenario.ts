export interface VariableOverride {
  variable_name: string;
  objective_coefficient?: number | null;
  lower_bound?: number | null;
  upper_bound?: number | null;
}

export interface ConstraintOverride {
  constraint_name: string;
  rhs?: number | null;
  operator?: "<=" | ">=" | "=" | null;
  coefficients?: Record<string, number> | null;
}

export interface ScenarioCreate {
  source_execution_id?: number;
  name: string;
  description?: string | null;

  variable_overrides: VariableOverride[];
  constraint_overrides: ConstraintOverride[];
}

export interface Scenario {
  id: number;
  problem_id: number;
  name: string;
  description: string | null;
  created_at: string;
  model_snapshot: Record<string, unknown>;
}

export interface ScenarioComparison {
  scenario_id: number;
  scenario_name: string;
  execution_id: number;
  status: string;
  objective_value: number | null;
  duration_ms: number;

  variables: Record<string, number>;
}

export interface ComparisonResponse {
  problem_id: number;

  scenarios: ScenarioComparison[];
}