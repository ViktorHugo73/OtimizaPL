import { apiRequest } from './client';
import type { ResourceAnalysis, ResourceComparison } from '../types/resources';
import type { ScenarioComparison } from '../types/scenario';

export function getExecutionResources(id: number, signal?: AbortSignal) {
  return apiRequest<ResourceAnalysis>(`/executions/${id}/resources`, { signal });
}

export function getScenarioResources(id: number, signal?: AbortSignal) {
  return apiRequest<ResourceAnalysis>(`/scenarios/${id}/resources`, { signal });
}

export function getResourceComparison(problemId: number, baseline: ScenarioComparison,
  target: ScenarioComparison, signal?: AbortSignal) {
  const query = new URLSearchParams({
    baseline_scenario_id: String(baseline.scenario_id),
    target_scenario_id: String(target.scenario_id),
    baseline_execution_id: String(baseline.execution_id),
    target_execution_id: String(target.execution_id),
  });
  return apiRequest<ResourceComparison>(`/problems/${problemId}/scenarios/compare/resources?${query}`, { signal });
}
