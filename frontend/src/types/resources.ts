export interface Resource {
  name: string;
  kind: 'constraint' | 'lower_bound' | 'upper_bound';
  operator: string;
  lhs: number;
  rhs: number;
  slack: number | null;
  excess: number | null;
  utilization_percent: number | null;
  is_active: boolean;
  is_feasible: boolean;
  potential_bottleneck: boolean;
}

export interface ResourceAnalysis {
  execution_id: number;
  scenario_id: number | null;
  problem_id: number;
  status: string;
  is_feasible: boolean;
  resources: Resource[];
}

export interface ResourceComparison {
  baseline: ResourceAnalysis;
  target: ResourceAnalysis;
  objective_comparable: boolean;
  objective_reason: string | null;
  objective_delta: number | null;
  objective_delta_percent: number | null;
  objective_improvement: number | null;
  resources: {
    name: string;
    kind: string;
    comparable: boolean;
    reason: string | null;
    lhs_delta: number | null;
    rhs_delta: number | null;
    slack_delta: number | null;
    excess_delta: number | null;
    utilization_delta_pp: number | null;
    activity_change: string | null;
    bottleneck_change: string | null;
  }[];
}
