export function statusLabel(status: string) {
  return ({ optimal: 'Solução ótima', infeasible: 'Problema inviável', unbounded: 'Problema ilimitado', iteration_limit: 'Limite de iterações', error: 'Falha na resolução' } as Record<string, string>)[status] ?? `Status não reconhecido (${status})`;
}

