const formatter = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 6 });
export function formatResource(value: number | null | undefined): string {
  return value == null ? 'Não se aplica' : formatter.format(Math.abs(value) < 0.0000005 ? 0 : value);
}
const kindNames: Record<string, string> = {
  constraint: 'Restrição', lower_bound: 'Limite inferior', upper_bound: 'Limite superior',
};
export function resourceLabel(name: string, kind: string) {
  return `${name} · ${kindNames[kind] ?? kind}`;
}

