import { apiRequest } from './client';
export interface ManagedItem { id: number; name: string; description: string | null }
export interface ProblemSummary extends ManagedItem { objective_type: string; created_at: string }
export type ManagedKind = 'problems' | 'scenarios';
export const listProblems = (signal?: AbortSignal) => apiRequest<ProblemSummary[]>('/problems', { signal });
export const editMetadata = (kind: ManagedKind, id: number, name: string, description: string | null) => apiRequest<ManagedItem>(`/${kind}/${id}`, { method: 'PATCH', body: JSON.stringify({ name, description }) });
export const deleteItem = (kind: ManagedKind, id: number) => apiRequest<void>(`/${kind}/${id}?confirm=true`, { method: 'DELETE' });
export const duplicateScenario = (id: number, name: string, description: string | null) => apiRequest<ManagedItem>(`/scenarios/${id}/duplicate`, { method: 'POST', body: JSON.stringify({ name, description }) });
