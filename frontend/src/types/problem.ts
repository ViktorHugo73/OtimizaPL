export interface Variable {
  id: number;
  name: string;
  description: string | null;
  objective_coefficient: number;
  lower_bound: number;
  upper_bound: number | null;
}

export interface ConstraintTerm {
  variable_id: number;
  variable_name: string;
  coefficient: number;
}

export interface Constraint {
  id: number;
  name: string;
  operator: "<=" | ">=" | "=";
  rhs: number;
  terms: ConstraintTerm[];
}

export interface Problem {
  id: number;
  name: string;
  description: string | null;
  objective_type: "min" | "max";
  variables: Variable[];
  constraints: Constraint[];
}

export interface VariableCreate {
  name: string;
  description?: string | null;
  objective_coefficient: number;
  lower_bound: number;
  upper_bound?: number | null;
}

export interface ConstraintTermCreate {
  variable_name: string;
  coefficient: number;
}

export interface ConstraintCreate {
  name: string;
  operator: "<=" | ">=" | "=";
  rhs: number;
  terms: ConstraintTermCreate[];
}

export interface ProblemCreate {
  name: string;
  description?: string | null;
  objective_type: "min" | "max";
  variables: VariableCreate[];
  constraints: ConstraintCreate[];
}