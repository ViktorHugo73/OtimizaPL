import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';

const source = readFileSync(new URL('./src/components/chartData.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } });
const { chartScale } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);

test('uses a common zero-based scale for positive values', () => {
  const scale = chartScale([50, 100]);
  assert.deepEqual(scale.bar(50), { left: 0, width: 50 });
});
test('places negative and positive values on opposite sides of zero', () => {
  const scale = chartScale([-20, 20]);
  assert.equal(scale.zero, 50);
  assert.deepEqual(scale.bar(-20), { left: 0, width: 50 });
  assert.deepEqual(scale.bar(20), { left: 50, width: 50 });
});
test('handles all zero and absent values without invalid geometry', () => {
  assert.deepEqual(chartScale([0, null]).bar(0), { left: 0, width: 0 });
  assert.equal(chartScale([null]).max, 0);
});
test('does not clip overutilization and keeps a 100% minimum scale', () => {
  assert.equal(chartScale([52.5], 100).max, 100);
  assert.equal(chartScale([125], 100).max, 125);
});
test('ignores nonfinite values when calculating scale', () => {
  assert.equal(chartScale([NaN, Infinity, 10]).max, 10);
});
