import type { ProblemCreate } from '../types/problem';

export type Operator = '<=' | '>=' | '=';
export interface Decision { id: string; name: string; description: string; cost: string; lower: string; upper: string }
export interface Condition { id: string; name: string; operator: Operator; rhs: string; coefficients: Record<string, string> }
export interface ProblemDraft { name: string; description: string; segment: string; objective: 'min' | 'max'; variables: Decision[]; constraints: Condition[] }
export interface FormIssue { key: string; step: number; message: string }
export const segments = ['Produção e serviços', 'Produção', 'Logística', 'Estoque', 'Serviços', 'Outros'];
export const steps = ['Identificação', 'Decisões', 'Objetivo', 'Restrições', 'Revisão'];
export const decision = (index: number): Decision => ({ id: crypto.randomUUID(), name: `X${index}`, description: '', cost: '0', lower: '0', upper: '' });
export const emptyDraft = (): ProblemDraft => ({ name: '', description: '', segment: '', objective: 'min', variables: [decision(1)], constraints: [] });
export const finiteNumber = (value: string) => value.trim() !== '' && Number.isFinite(Number(value));

export function validateDraft(draft: ProblemDraft): FormIssue[] {
  const issues: FormIssue[] = [];
  const add = (key: string, step: number, message: string) => issues.push({ key, step, message });
  if (!draft.name.trim()) add('name', 0, 'Informe o nome do problema.');
  else if (draft.name.trim().length > 150) add('name', 0, 'Use até 150 caracteres.');
  if (draft.segment && !segments.includes(draft.segment)) add('segment', 0, 'Selecione um segmento da lista.');
  if (!draft.variables.length) add('variables', 1, 'Adicione pelo menos uma variável.');
  const names = draft.variables.map(v => v.name.trim());
  draft.variables.forEach(v => {
    if (!v.name.trim()) add(`v-${v.id}-name`, 1, 'Informe o nome da decisão.');
    else if (v.name.trim().length > 100) add(`v-${v.id}-name`, 1, 'Use até 100 caracteres.');
    else if (names.filter(n => n === v.name.trim()).length > 1) add(`v-${v.id}-name`, 1, 'Este nome já está em uso.');
    if (!finiteNumber(v.lower) || Number(v.lower) < 0) add(`v-${v.id}-lower`, 1, 'Informe um número finito maior ou igual a zero.');
    if (v.upper.trim() && (!finiteNumber(v.upper) || Number(v.upper) < Number(v.lower))) add(`v-${v.id}-upper`, 1, 'Informe um número finito maior ou igual ao limite inferior.');
    if (!finiteNumber(v.cost)) add(`v-${v.id}-cost`, 2, 'Informe um valor numérico finito.');
  });
  if (!['min', 'max'].includes(draft.objective)) add('objective', 2, 'Selecione minimizar ou maximizar.');
  if (!draft.constraints.length) add('constraints', 3, 'Adicione pelo menos uma condição.');
  const conditionNames = draft.constraints.map(c => c.name.trim());
  draft.constraints.forEach(c => {
    if (!c.name.trim()) add(`c-${c.id}-name`, 3, 'Informe o nome da condição.');
    else if (c.name.trim().length > 150) add(`c-${c.id}-name`, 3, 'Use até 150 caracteres.');
    else if (conditionNames.filter(n => n === c.name.trim()).length > 1) add(`c-${c.id}-name`, 3, 'Este nome já está em uso.');
    if (!['<=', '>=', '='].includes(c.operator)) add(`c-${c.id}-operator`, 3, 'Selecione uma relação válida.');
    if (!finiteNumber(c.rhs)) add(`c-${c.id}-rhs`, 3, 'Informe um valor numérico finito.');
    draft.variables.forEach(v => {
      if (!finiteNumber(c.coefficients[v.id] ?? '')) add(`c-${c.id}-${v.id}`, 3, `Informe a contribuição de ${v.name || 'esta variável'}.`);
    });
    if (Object.keys(c.coefficients).some(id => !draft.variables.some(v => v.id === id))) add(`c-${c.id}-name`, 3, 'Há coeficientes sem uma variável correspondente.');
  });
  return issues;
}

export function addDecision(draft: ProblemDraft): ProblemDraft {
  let index = draft.variables.length + 1;
  while (draft.variables.some(v => v.name.trim() === `X${index}`)) index++;
  const v = decision(index);
  return { ...draft, variables: [...draft.variables, v], constraints: draft.constraints.map(c => ({ ...c, coefficients: { ...c.coefficients, [v.id]: '0' } })) };
}

export function removeDecision(draft: ProblemDraft, id: string): ProblemDraft {
  if (draft.variables.length <= 1) return draft;
  return { ...draft, variables: draft.variables.filter(v => v.id !== id), constraints: draft.constraints.map(c => {
    const coefficients = { ...c.coefficients }; delete coefficients[id]; return { ...c, coefficients };
  }) };
}

export function toPayload(draft: ProblemDraft): ProblemCreate {
  if (validateDraft(draft).length) throw new Error('Revise os campos antes de salvar.');
  return {
    name: draft.name.trim(), description: [draft.segment ? `Segmento: ${draft.segment}` : '', draft.description.trim()].filter(Boolean).join('\n\n') || null,
    objective_type: draft.objective,
    variables: draft.variables.map(v => ({ name: v.name.trim(), description: v.description.trim() || null, objective_coefficient: Number(v.cost), lower_bound: Number(v.lower), upper_bound: v.upper.trim() ? Number(v.upper) : null })),
    constraints: draft.constraints.map(c => ({ name: c.name.trim(), operator: c.operator, rhs: Number(c.rhs), terms: draft.variables.map(v => ({ variable_name: v.name.trim(), coefficient: Number(c.coefficients[v.id]) })) })),
  };
}

export function fromPayload(payload: ProblemCreate): ProblemDraft {
  const variables = payload.variables.map(v => ({ id: crypto.randomUUID(), name: v.name, description: v.description ?? '', cost: String(v.objective_coefficient), lower: String(v.lower_bound), upper: v.upper_bound == null ? '' : String(v.upper_bound) }));
  return { name: payload.name, description: payload.description ?? '', segment: '', objective: payload.objective_type, variables,
    constraints: payload.constraints.map(c => ({ id: crypto.randomUUID(), name: c.name, operator: c.operator, rhs: String(c.rhs), coefficients: Object.fromEntries(variables.map(v => [v.id, String(c.terms.find(t => t.variable_name === v.name)?.coefficient ?? 0)])) })) };
}

export function expression(variables: Decision[], coefficients: Record<string, string>): string {
  return variables.map((v, i) => {
    const raw = coefficients[v.id] ?? '';
    const value = finiteNumber(raw) ? Number(raw) : null;
    const sign = value !== null && value < 0 ? '−' : i > 0 ? '+' : '';
    return `${sign} ${value === null ? '?' : Math.abs(value).toLocaleString('pt-BR', { maximumSignificantDigits: 15 })} × ${v.name.trim() || '?'}`.trim();
  }).join(' ');
}
