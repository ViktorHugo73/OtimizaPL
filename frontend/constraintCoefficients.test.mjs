import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
const source = readFileSync(new URL('./src/components/constraintCoefficients.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } });
const { parseCoefficients } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
test('preserves zero, negative and fractional coefficients', () => {
  assert.deepEqual(parseCoefficients({ XR: '0', XS: '-0.25', Z: '1.5' }, 'Horas'), { XR: 0, XS: -0.25, Z: 1.5 });
});
for (const text of ['', ' ', 'NaN', 'Infinity', '1e999']) {
  test(`rejects invalid input ${JSON.stringify(text)} without converting to zero`, () => {
    assert.throws(() => parseCoefficients({ XR: text }, 'Horas'), /XR.*Horas/);
  });
}
