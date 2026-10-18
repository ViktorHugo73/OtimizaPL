import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import springCostJson from '../../../examples/feixe_molas_custo.json?raw';
import mixProductionJson from '../../../examples/mix_producao.json?raw';
import { createProblem, solveProblem } from '../api/problems';
import type { ProblemCreate } from '../types/problem';
import ProblemField from '../components/ProblemField';
import { addDecision, emptyDraft, expression, fromPayload, removeDecision, segments, steps, toPayload, validateDraft } from '../components/problemForm';
import type { Condition, Decision } from '../components/problemForm';
import './createProblem.css';

export default function CreateProblemPage() {
  const navigate = useNavigate();
  const [draft, setDraft] = useState(emptyDraft);
  const [draftNotice, setDraftNotice] = useState('');
  function saveLocalDraft() {
    try { localStorage.setItem('tcc-problem-draft-v1', JSON.stringify({ version: 1, draft })); setDraftNotice('Rascunho salvo neste navegador.'); }
    catch { setDraftNotice('Não foi possível salvar no navegador. Verifique a disponibilidade do armazenamento local.'); }
  }
  function restoreLocalDraft() {
    try { const raw = localStorage.getItem('tcc-problem-draft-v1'); if (!raw) { setDraftNotice('Nenhum rascunho salvo neste navegador.'); return; } const record = JSON.parse(raw); if (record.version !== 1) throw new Error(); const restored = record.draft; if (typeof restored.name !== 'string' || typeof restored.description !== 'string' || typeof restored.segment !== 'string' || !['min', 'max'].includes(restored.objective) || !Array.isArray(restored.variables) || !Array.isArray(restored.constraints) || !restored.variables.every((v: Decision) => ['id', 'name', 'description', 'cost', 'lower', 'upper'].every(k => typeof v[k as keyof Decision] === 'string')) || !restored.constraints.every((c: Condition) => typeof c.id === 'string' && typeof c.name === 'string' && typeof c.rhs === 'string' && ['<=', '>=', '='].includes(c.operator) && c.coefficients && Object.values(c.coefficients).every(value => typeof value === 'string'))) throw new Error(); validateDraft(restored); setDraft(restored); setStep(0); setChecked([]); setDraftNotice('Rascunho recuperado.'); }
    catch { setDraftNotice('Não foi possível recuperar o rascunho deste navegador.'); }
  }
  const [step, setStep] = useState(0);
  const [checked, setChecked] = useState<number[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [savedId, setSavedId] = useState<number | null>(null);
  const lock = useRef(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const form = useRef<HTMLFormElement>(null);
  const issues = validateDraft(draft);
  const errorFor = (key: string) => issues.find(i => i.key === key && checked.includes(i.step))?.message;
  const costs = Object.fromEntries(draft.variables.map(v => [v.id, v.cost]));
  const move = (target: number) => { setStep(target); setMessage(''); requestAnimationFrame(() => heading.current?.focus()); };

  function go(target: number) {
    if (busy) return;
    if (target <= step) { move(target); return; }
    setChecked(old => [...new Set([...old, ...Array.from({ length: target }, (_, i) => i)])]);
    const first = issues.find(i => i.step < target);
    if (first) {
      setStep(first.step); setMessage('Revise os campos indicados para continuar.');
      requestAnimationFrame(() => document.getElementById(first.key)?.focus());
    } else move(target);
  }

  const changeVariable = (id: string, field: keyof Omit<Decision, 'id'>, value: string) => setDraft(d => ({ ...d, variables: d.variables.map(v => v.id === id ? { ...v, [field]: value } : v) }));
  const changeCondition = (id: string, field: 'name' | 'rhs' | 'operator', value: string) => setDraft(d => ({ ...d, constraints: d.constraints.map(c => c.id === id ? { ...c, [field]: value } : c) }));
  function addCondition() {
    let index = draft.constraints.length + 1;
    while (draft.constraints.some(c => c.name.trim() === `Condição ${index}`)) index++;
    const c: Condition = { id: crypto.randomUUID(), name: `Condição ${index}`, operator: '<=', rhs: '0', coefficients: Object.fromEntries(draft.variables.map(v => [v.id, '0'])) };
    setDraft(d => ({ ...d, constraints: [...d.constraints, c] }));
  }

  async function save(resolve: boolean) {
    if (lock.current) return;
    setChecked([0, 1, 2, 3]);
    if (issues.length) { setStep(issues[0].step); setMessage('Revise os campos indicados antes de salvar.'); requestAnimationFrame(() => document.getElementById(issues[0].key)?.focus()); return; }
    lock.current = true; setBusy(true); setMessage('');
    let id = savedId;
    try {
      if (id === null) { const created = await createProblem(toPayload(draft)); id = created.id; setSavedId(id); }
      if (resolve) {
        const result = await solveProblem(id);
        navigate(`/problems/${id}/executions?execution=${result.execution_id}`);
      } else navigate(`/problems/${id}`);
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : 'Não foi possível concluir a solicitação.';
      setMessage(id === null ? `${detail} Se houve perda de conexão, confira a lista de problemas antes de repetir o salvamento.` : `Problema #${id} salvo. Não foi possível confirmar a resolução: ${detail} Confira o histórico antes de tentar resolver novamente.`);
    } finally { setBusy(false); lock.current = false; }
  }

  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (step < 4) go(step + 1); else void save(false); }
  const numeric = { type: 'number', step: 'any' } as const;

  return <main className="problem-create problem-wizard">
    <header className="wizard-header"><div><h1>Novo problema</h1><p className="wizard-counter">Etapa {step + 1} de 5 — {steps[step]}</p></div></header>
    <nav aria-label="Etapas do cadastro"><ol className="wizard-progress">{steps.map((label, index) => <li key={label} className={index <= step ? 'is-reached' : undefined}>
      <button type="button" disabled={busy || index > step} aria-current={index === step ? 'step' : undefined} onClick={() => go(index)}>{label}</button>
    </li>)}</ol></nav>
    <form ref={form} noValidate onSubmit={submit} aria-busy={busy}>
      <section className="problem-create-section" aria-labelledby="wizard-heading">
        <h2 ref={heading} id="wizard-heading" tabIndex={-1}>{['Identifique o projeto', 'O que o sistema deve decidir?', 'Qual resultado deseja otimizar?', 'Defina os limites da operação', 'Revise o problema'][step]}</h2>
        <p className="problem-create-help">{['Essas informações facilitam a organização e a localização dos modelos cadastrados.', 'Cadastre as quantidades que serão calculadas pela otimização. Cada decisão corresponde a uma variável do modelo.', 'Escolha a finalidade do cálculo e informe a contribuição de cada decisão para o resultado total.', 'Informe as condições que a solução deverá respeitar, como demanda mínima, capacidade de máquinas e recursos disponíveis.', 'Confira os dados antes de salvar e enviar para otimização.'][step]}</p>
        <fieldset className="wizard-content" disabled={busy || savedId !== null}>
          <legend className="wizard-sr-only">{steps[step]}</legend>
          {step === 0 && <div className="problem-create-grid problem-create-general">
            <ProblemField id="name" label="Nome do problema" error={errorFor('name')}>{props => <input {...props} required maxLength={150} value={draft.name} onChange={e => setDraft(d => ({ ...d, name: e.target.value }))} placeholder="Ex.: Planejamento de produção" />}</ProblemField>
            <ProblemField id="description" label="Descrição">{props => <textarea {...props} placeholder="Qual decisão você deseja melhorar?" rows={3} value={draft.description} onChange={e => setDraft(d => ({ ...d, description: e.target.value }))} />}</ProblemField>
            <ProblemField id="segment" label="Segmento de aplicação" hint="A categoria serve para organizar os projetos e não limita o modelo matemático. Será incluída na descrição." error={errorFor('segment')}>{props => <select {...props} value={draft.segment} onChange={e => setDraft(d => ({ ...d, segment: e.target.value }))}><option value="">Não informado</option>{segments.map(s => <option key={s}>{s}</option>)}</select>}</ProblemField>
            <details className="wizard-extras"><summary>Recuperar rascunho ou carregar exemplo</summary><button type="button" onClick={() => { if (window.confirm('Substituir os campos pelo rascunho salvo?')) restoreLocalDraft(); }}>Recuperar rascunho</button><button type="button" onClick={() => { if (window.confirm('Substituir os campos pelo exemplo de feixe de molas?')) { setDraft(fromPayload(JSON.parse(springCostJson) as ProblemCreate)); setChecked([]); setMessage(''); } }}>Carregar exemplo: custo de feixe de molas</button><button type="button" onClick={() => { if (window.confirm('Substituir os campos pelo exemplo?')) { setDraft(fromPayload(JSON.parse(mixProductionJson) as ProblemCreate)); setChecked([]); } }}>Carregar exemplo de validação: mix de produção</button></details>
          </div>}

          {step === 1 && <>

            <div className="problem-create-items">{draft.variables.map((v, index) => <fieldset key={v.id} className="problem-create-item"><legend>Decisão {index + 1}</legend>
              <div className="problem-create-grid">
                <ProblemField id={`v-${v.id}-name`} label="Nome da decisão" error={errorFor(`v-${v.id}-name`)}>{props => <input {...props} required maxLength={100} placeholder="Ex.: Quantidade produzida" value={v.name} onChange={e => changeVariable(v.id, 'name', e.target.value)} />}</ProblemField>
              </div>
              <p className="wizard-hint">Quantidade não negativa, podendo assumir valores decimais.</p>
              <details className="wizard-extras" open={Boolean(errorFor(`v-${v.id}-lower`) || errorFor(`v-${v.id}-upper`)) || undefined}><summary>Descrição e limites opcionais</summary>
                <ProblemField id={`v-${v.id}-description`} label="Descrição da decisão">{props => <input {...props} value={v.description} onChange={e => changeVariable(v.id, 'description', e.target.value)} />}</ProblemField>
                <div className="problem-create-grid wizard-two-columns"><ProblemField id={`v-${v.id}-lower`} label="Quantidade mínima" error={errorFor(`v-${v.id}-lower`)}>{props => <input {...props} {...numeric} value={v.lower} onChange={e => changeVariable(v.id, 'lower', e.target.value)} />}</ProblemField><ProblemField id={`v-${v.id}-upper`} label="Quantidade máxima (opcional)" error={errorFor(`v-${v.id}-upper`)}>{props => <input {...props} {...numeric} value={v.upper} onChange={e => changeVariable(v.id, 'upper', e.target.value)} placeholder="Sem limite" />}</ProblemField></div>
              </details>
              <div className="problem-create-item-actions"><button type="button" disabled={draft.variables.length === 1} onClick={() => { if (window.confirm(`Excluir ${v.name || 'esta variável'} e suas contribuições no objetivo e nas condições?`)) setDraft(d => removeDecision(d, v.id)); }} aria-label={`Excluir decisão ${index + 1}`}>Excluir</button></div>
            </fieldset>)}</div>
            <button type="button" onClick={() => setDraft(addDecision)} className="wizard-add">＋ Adicionar decisão</button>

          </>}

          {step === 2 && <>
            <fieldset className="wizard-objective"><legend>Tipo de otimização</legend>{(['min', 'max'] as const).map(value => <label key={value}><input type="radio" name="objective" value={value} checked={draft.objective === value} onChange={() => setDraft(d => ({ ...d, objective: value }))} />{value === 'min' ? 'Minimizar — reduzir custos, tempo ou consumo' : 'Maximizar — aumentar lucro, produção ou retorno'}</label>)}</fieldset>
            <div className="problem-create-grid problem-create-coefficients">{draft.variables.map(v => <ProblemField key={v.id} id={`v-${v.id}-cost`} label={`${v.name} — contribuição por unidade`} hint={v.description || undefined} error={errorFor(`v-${v.id}-cost`)}>{props => <input {...props} {...numeric} required value={v.cost} onChange={e => changeVariable(v.id, 'cost', e.target.value)} />}</ProblemField>)}</div>
            <div className="wizard-preview"><h3>Objetivo configurado</h3><p>{draft.objective === 'min' ? 'Minimizar' : 'Maximizar'} o resultado total calculado a partir dos valores informados.</p></div>
          </>}

          {step === 3 && <>

            {draft.constraints.length === 0 && <p id="constraints" tabIndex={-1} className={errorFor('constraints') ? 'wizard-field-error' : 'problem-create-empty'}>{errorFor('constraints') || 'Nenhuma condição cadastrada.'}</p>}
            <div className="problem-create-items">{draft.constraints.map((c, index) => <fieldset key={c.id} className="problem-create-item"><legend>Condição {index + 1}</legend>
                <ProblemField id={`c-${c.id}-name`} label="Nome da condição" error={errorFor(`c-${c.id}-name`)}>{props => <input {...props} required maxLength={150} placeholder="Ex.: Horas disponíveis" value={c.name} onChange={e => changeCondition(c.id, 'name', e.target.value)} />}</ProblemField>
              <p className="wizard-hint">Consumo ou contribuição por unidade</p>
              <div className="problem-create-grid wizard-two-columns">{draft.variables.map(v => <div key={v.id}><ProblemField id={`c-${c.id}-${v.id}`} label={v.name} error={errorFor(`c-${c.id}-${v.id}`)}>{props => <input {...props} {...numeric} required value={c.coefficients[v.id] ?? ''} onChange={e => setDraft(d => ({ ...d, constraints: d.constraints.map(item => item.id === c.id ? { ...item, coefficients: { ...item.coefficients, [v.id]: e.target.value } } : item) }))} />}</ProblemField></div>)}</div>
              <div className="problem-create-grid wizard-two-columns">                <ProblemField id={`c-${c.id}-operator`} label="Condição" error={errorFor(`c-${c.id}-operator`)}>{props => <select {...props} value={c.operator} onChange={e => changeCondition(c.id, 'operator', e.target.value)}><option value="<=">No máximo (≤)</option><option value=">=">No mínimo (≥)</option><option value="=">Exatamente (=)</option></select>}</ProblemField>
                <ProblemField id={`c-${c.id}-rhs`} label="Limite" error={errorFor(`c-${c.id}-rhs`)}>{props => <input {...props} {...numeric} required value={c.rhs} onChange={e => changeCondition(c.id, 'rhs', e.target.value)} />}</ProblemField>
</div>
              <div className="problem-create-item-actions"><button type="button" onClick={() => { if (window.confirm(`Excluir a condição ${c.name || index + 1} e seus coeficientes?`)) setDraft(d => ({ ...d, constraints: d.constraints.filter(item => item.id !== c.id) })); }} aria-label={`Excluir condição ${index + 1}`}>Excluir</button></div>
            </fieldset>)}</div>
            <button type="button" onClick={addCondition} className="wizard-add">＋ Adicionar condição</button>
          </>}

          {step === 3 && <p className="wizard-hint">Todas as decisões são consideradas não negativas. O cadastro inicial admite apenas relações lineares.</p>}
          {step === 4 && <div className="wizard-review">
            <h3>{draft.name}</h3><p>Segmento: {draft.segment || 'Não informado'}</p><p className="wizard-description">{draft.description || 'Sem descrição.'}</p>
            <dl className="wizard-summary"><dt>Objetivo</dt><dd>{draft.objective === 'min' ? 'Minimização' : 'Maximização'}</dd><dt>Decisões</dt><dd>{draft.variables.length}</dd><dt>Restrições</dt><dd>{draft.constraints.length}</dd></dl><h3>Função objetivo</h3><p className="wizard-formula">{draft.objective === 'min' ? 'Min' : 'Max'} Z = {expression(draft.variables, costs)}</p>
            <details><summary>Decisões e limites</summary><ul>{draft.variables.map(v => <li key={v.id}><strong>{v.name}</strong>{v.description ? ` — ${v.description}` : ''}: mínimo {v.lower}; máximo {v.upper.trim() || 'sem limite'}.</li>)}</ul></details>
            <h3>Condições cadastradas</h3><ul>{draft.constraints.map(c => <li key={c.id}><strong>{c.name}</strong>: {expression(draft.variables, c.coefficients)} {c.operator === '<=' ? '≤' : c.operator === '>=' ? '≥' : '='} {c.rhs}</li>)}</ul>
            <details><summary>Visualização matemática complementar</summary><p>{draft.objective === 'min' ? 'min' : 'max'} Z = {expression(draft.variables, costs)}</p>{draft.constraints.map(c => <p key={c.id}>{expression(draft.variables, c.coefficients)} {c.operator} {c.rhs}</p>)}{draft.variables.map(v => <p key={v.id}>{v.lower} ≤ {v.name}{v.upper.trim() ? ` ≤ ${v.upper}` : ''}; variável contínua.</p>)}</details>
            <p className="wizard-valid">✓ Cadastro estruturalmente válido para envio à otimização.</p>
          </div>}
        </fieldset>
      </section>
      {message && <div className="problem-create-error" role="alert"><p>{message}</p>{savedId ? <p><Link to={`/problems/${savedId}`}>Abrir problema salvo</Link> · <Link to={`/problems/${savedId}/executions`}>Consultar histórico</Link></p> : <Link to="/problems">Consultar problemas cadastrados</Link>}</div>}
      {busy && <p role="status">{savedId ? 'Resolvendo o problema…' : 'Salvando o problema…'}</p>}
      {draftNotice && <p role="status">{draftNotice}</p>}
      <div className="wizard-navigation"><button type="button" disabled={busy || savedId !== null} onClick={saveLocalDraft}>Salvar rascunho</button><div className="wizard-nav-right">
        <button type="button" disabled={step === 0 || busy} onClick={() => go(step - 1)}>Voltar</button>
        {step < 4 ? <button className="wizard-primary" type="submit" disabled={busy}>Continuar</button> : <div className="wizard-save-actions">
          <button type="submit" disabled={busy}>{savedId ? 'Abrir problema salvo' : 'Salvar'}</button>
          <button className="wizard-primary" type="button" disabled={busy} onClick={() => void save(true)}>{savedId ? 'Tentar resolver novamente' : 'Salvar e resolver'}</button>
        </div>}
      </div></div>
    </form>
  </main>;
}
