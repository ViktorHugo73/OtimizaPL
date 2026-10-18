import { apiRequest } from './client';
import type { SolveResult } from '../types/optimization';

export interface ExecutionHistoryItem extends SolveResult {
  created_at: string;
  problem_name: string | null;
  objective_type: 'min' | 'max' | null;
  snapshot_available: boolean;
  recorded_variables: { name: string; value: number }[] | null;
}

export function getExecutionHistory(problemId: number, signal?: AbortSignal) {
  return apiRequest<ExecutionHistoryItem[]>(`/problems/${problemId}/executions`, { signal });
}
