export function chartScale(values: (number | null)[], minimumMaximum = 0) {
  const finite = values.filter((value): value is number => value !== null && Number.isFinite(value));
  const min = Math.min(0, ...finite);
  const max = Math.max(minimumMaximum, 0, ...finite);
  const span = max - min || 1;
  return { min, max, zero: -min / span * 100,
    bar(value: number) {
      return { left: (Math.min(value, 0) - min) / span * 100, width: Math.abs(value) / span * 100 };
    } };
}
