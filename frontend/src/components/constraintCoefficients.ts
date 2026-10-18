export function parseCoefficients(values: Record<string, string>, constraintName: string): Record<string, number> {
  return Object.fromEntries(Object.entries(values).map(([variable, text]) => {
    const value = Number(text);
    if (!text.trim() || !Number.isFinite(value)) {
      throw new Error(`Informe um coeficiente numérico válido para ${variable} em “${constraintName}”.`);
    }
    return [variable, value];
  }));
}
