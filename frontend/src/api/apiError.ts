export function apiErrorMessage(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail;
  if (!Array.isArray(detail)) return fallback;
  const names: Record<string, string> = { name: 'Nome', description: 'Descrição', variables: 'Variáveis', constraints: 'Condições', objective_type: 'Objetivo', objective_coefficient: 'Contribuição', lower_bound: 'Quantidade mínima', upper_bound: 'Quantidade máxima', rhs: 'Valor do limite', operator: 'Relação', terms: 'Contribuições', coefficient: 'Coeficiente', variable_name: 'Variável' };
  const messages = detail.flatMap((item: unknown) => {
    if (!item || typeof item !== 'object' || !('msg' in item) || typeof item.msg !== 'string') return [];
    const location = 'loc' in item && Array.isArray(item.loc) ? item.loc.filter(part => part !== 'body').map(part => typeof part === 'number' ? `item ${part + 1}` : names[String(part)] ?? String(part)).join(' / ') : '';
    return [location ? `${location}: ${item.msg}` : item.msg];
  });
  return messages.length ? messages.join('; ') : fallback;
}
