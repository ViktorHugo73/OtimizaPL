export interface VariableResult {
  variable_id: number;
  variable_name: string;
  value: number;
}

export interface SolveResult {
  execution_id: number;
  problem_id: number;
  status: string;
  objective_value: number | null;
  iterations_phase1: number;
  iterations_phase2: number;
  duration_ms: number;
  solver_version: string;
  variables: VariableResult[];
}