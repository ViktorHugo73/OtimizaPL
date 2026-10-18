import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { addDecision, emptyDraft, fromPayload, removeDecision, toPayload, validateDraft } from '../src/components/problemForm.ts';
import { apiErrorMessage } from '../src/api/apiError.ts';
const fixture = JSON.parse(readFileSync(new URL('../../examples/mix_producao.json', import.meta.url)));

test('exemplo com três variáveis preserva o contrato da API', () => {
  const d = fromPayload(fixture);
  assert.equal(validateDraft(d).length, 0);
  const expected = structuredClone(fixture);
  expected.constraints = expected.constraints.map(c => ({ ...c, terms: expected.variables.map(v => ({ variable_name: v.name, coefficient: c.terms.find(t => t.variable_name === v.name)?.coefficient ?? 0 })) }));
  assert.deepEqual(toPayload(d), expected);
});
test('renomear usa IDs estáveis e adicionar/remover sincroniza toda a matriz', () => {
  let d = fromPayload(fixture);
  const id = d.variables[0].id;
  const previous = d.constraints[0].coefficients[id];
  d.variables[0].name = 'REFORMAS';
  assert.equal(toPayload(d).constraints[0].terms[0].variable_name, 'REFORMAS');
  assert.equal(d.constraints[0].coefficients[id], previous);
  d = addDecision(d);
  const added = d.variables.at(-1).id;
  assert.ok(d.constraints.every(c => c.coefficients[added] === '0'));
  d = removeDecision(d, id);
  assert.ok(d.constraints.every(c => !(id in c.coefficients)));
  assert.equal(validateDraft(d).length, 0);
});
test('excluir um nome padrão não provoca duplicação ao adicionar', () => {
  let d = addDecision(addDecision(emptyDraft()));
  d = removeDecision(d, d.variables[1].id);
  d = addDecision(d);
  assert.equal(new Set(d.variables.map(v => v.name)).size, 3);
});
test('campos vazios, duplicados, não finitos e limites inconsistentes são rejeitados', () => {
  const d = fromPayload(fixture);
  d.name = ' ';
  d.variables[1].name = d.variables[0].name;
  d.variables[0].cost = '';
  d.variables[1].lower = '-1';
  d.variables[2].upper = 'Infinity';
  d.constraints[0].rhs = 'NaN';
  delete d.constraints[1].coefficients[d.variables[0].id];
  const errors = validateDraft(d);
  assert.equal(errors.length, 8);
  assert.throws(() => toPayload(d));
});
test('segmento é persistido na descrição sem introduzir campos no contrato', () => {
  const d = fromPayload(fixture); d.segment = 'Serviços';
  const p = toPayload(d);
  assert.ok(p.description.startsWith('Segmento: Serviços\n\n'));
  assert.equal('segment' in p, false);
});
test('modelo inviável permanece válido para envio ao solver', () => {
  const d = fromPayload(fixture); d.variables[0].lower = '5';
  assert.equal(validateDraft(d).length, 0);
  assert.equal(toPayload(d).variables[0].lower_bound, 5);
});
test('upper_bound vazio é nulo, coeficientes negativos e zero são preservados', () => {
  const d = fromPayload(fixture); d.variables[0].cost = '-3';
  assert.equal(toPayload(d).variables[0].upper_bound, null);
  assert.equal(toPayload(d).variables[0].objective_coefficient, -3);
  assert.equal(toPayload(d).constraints[0].terms[1].coefficient, 0);
});
test('erros Pydantic são legíveis e incluem localização do campo', () => {
  assert.equal(apiErrorMessage([{loc:['body','variables',0,'name'],msg:'Field required'}], 'HTTP 422'), 'Variáveis / item 1 / Nome: Field required');
  assert.equal(apiErrorMessage('Erro de negócio', 'HTTP 400'), 'Erro de negócio');
  assert.equal(apiErrorMessage({}, 'HTTP 500'), 'HTTP 500');
});
