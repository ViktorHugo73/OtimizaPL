import { statusLabel } from './executionFormatting';
import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import type { ExecutionHistoryItem } from '../api/executions';
import { createScenario } from '../api/scenarios';
import { getExecutionResources } from '../api/resources';
import type { ResourceAnalysis } from '../types/resources';
import { ResourceTable } from './ResourceAnalysis';
import { formatResource, resourceLabel } from './resourceFormatting';
import './executionResult.css';

export default function ExecutionResult({ execution: e }: { execution: ExecutionHistoryItem }) {
  const [analysis, setAnalysis] = useState<ResourceAnalysis | null>(null);
  const [error, setError] = useState('');
  const [scenarioName, setScenarioName] = useState(`Cenário da execução ${e.execution_id}`);
  const [creating, setCreating] = useState(false);
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [scenarioError, setScenarioError] = useState('');
  const lock = useRef(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const technical = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    heading.current?.focus();
    if (e.status !== 'optimal') return;
    const controller = new AbortController();
    getExecutionResources(e.execution_id, controller.signal).then(data => {
      if (!controller.signal.aborted) setAnalysis(data);
    }).catch(reason => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Falha ao consultar recursos.'); });
    return () => controller.abort();
  }, [e.execution_id, e.status]);
  const optimal = e.status === 'optimal';
  const direction = e.objective_type === 'min' ? 'Minimização' : e.objective_type === 'max' ? 'Maximização' : 'Sentido não registrado';
  const variables = e.recorded_variables;
  const constraints = analysis?.resources.filter(row => row.kind === 'constraint') ?? [];
  const active = constraints.filter(row => row.is_active);
  const fullyUsed = constraints.filter(row => row.is_feasible && row.is_active && row.utilization_percent !== null);
  const available = constraints.filter(row => row.is_feasible && !row.is_active && row.utilization_percent !== null && row.slack !== null && row.slack > 0);
  async function clone() {
    if (lock.current || !scenarioName.trim()) return;
    lock.current = true; setCreating(true); setScenarioError('');
    try {
      const scenario = await createScenario(e.problem_id, { name: scenarioName.trim(), source_execution_id: e.execution_id, variable_overrides: [], constraint_overrides: [] });
      setScenarioId(scenario.id);
    } catch (reason) { setScenarioError(`${reason instanceof Error ? reason.message : 'Falha ao criar cenário.'} Confira os cenários antes de repetir caso tenha ocorrido perda de conexão.`); }
    finally { lock.current = false; setCreating(false); }
  }
  return <section className="execution-result" aria-label={`Detalhes da execução ${e.execution_id}`}>
    <header className="result-header"><div><p>{e.problem_name ?? `Problema #${e.problem_id}`} <small>(nome atual)</small></p><h2 ref={heading} tabIndex={-1}>Execução #{e.execution_id}</h2><p>{new Date(e.created_at).toLocaleString('pt-BR', { timeZoneName: 'short' })}</p></div><span className="result-status">{statusLabel(e.status)}</span></header>
    <nav className="result-actions"><Link to={`/problems/${e.problem_id}`}>Voltar ao problema</Link><Link to={`/problems/${e.problem_id}/executions`}>Consultar histórico</Link><button type="button" onClick={() => { if (technical.current) { technical.current.open = true; technical.current.scrollIntoView({ behavior: 'smooth' }); technical.current.querySelector('summary')?.focus(); } }}>Visualizar detalhes técnicos</button></nav>
    <div className="result-objective"><span>{optimal ? 'Valor ótimo da função objetivo' : 'Valor ótimo indisponível'} · {direction}</span><strong>{optimal && e.objective_value !== null ? formatResource(e.objective_value) : '—'}</strong></div>
    {optimal && variables && <><h3>Decisões calculadas</h3><div className="result-cards">{variables.map(v => <article key={v.name}><h4>{v.name}</h4><strong>{formatResource(v.value)}</strong></article>)}</div></>}
    <section className="result-summary" aria-label="Interpretação do resultado"><h3>O que este resultado significa?</h3>
      {optimal && <>
        {analysis && !analysis.is_feasible ? <p>O sistema informou uma solução ótima, mas a verificação identificou condições não atendidas. Não é possível confirmar a viabilidade dos valores apresentados.</p> : <p>
          {`O sistema determinou ${variables?.length ? variables.map(v => `${v.name} = ${formatResource(v.value)}`).join(' e ') : 'uma solução ótima'}${e.objective_value !== null ? `, resultando no valor ${e.objective_type === 'min' ? 'mínimo' : e.objective_type === 'max' ? 'máximo' : 'ótimo'} de ${formatResource(e.objective_value)}` : ''}. `}
          {analysis?.is_feasible && <>
            {active.length ? `As restrições ${active.map(r => `“${r.name}”`).join(' e ')} estão ativas, ou seja, foram atendidas no limite. ` : 'Nenhuma restrição cadastrada foi atendida no limite. '}
            {available.length > 0 && `Ainda há capacidade disponível em ${available.map(r => `“${r.name}”`).join(', ')}. `}
            {fullyUsed.length > 0 && `Para os parâmetros considerados, a solução utiliza toda a capacidade de ${fullyUsed.map(r => `“${r.name}”`).join(' e ')}. `}
            {'Essa combinação atende às condições do modelo com o melhor valor da função objetivo.'}
          </>}
        </p>}
        {!variables && <p>Os valores históricos das decisões não estão disponíveis para detalhar esta interpretação.</p>}
        {!analysis && <p>{error ? 'A análise dos recursos não está disponível para complementar a interpretação.' : 'Conferindo as restrições e a utilização dos recursos…'}</p>}
      </>}
      {e.status === 'infeasible' && <p>Não existe uma combinação de valores para as decisões que atenda a todas as condições cadastradas ao mesmo tempo. Por isso, o modelo é inviável e não há uma solução ótima para apresentar.</p>}
      {e.status === 'unbounded' && <p>Nas condições cadastradas, a função objetivo pode continuar melhorando sem atingir um limite finito. Por isso, o modelo é ilimitado e não há um valor ótimo finito para apresentar.</p>}
      {!['optimal', 'infeasible', 'unbounded'].includes(e.status) && <p>{statusLabel(e.status)}. Não há uma solução ótima confirmada para interpretar.</p>}
    </section>
    {optimal && <section><h3>Análise de recursos</h3>{error ? <p role="alert">Análise histórica indisponível: {error}</p> : !analysis ? <p role="status">Carregando análise de recursos…</p> : <>
      <p>Uma restrição ativa está no limite dentro da tolerância numérica. Um gargalo potencial é uma classificação distinta; ampliar a capacidade não garante melhora do resultado.</p>
      <div className="result-cards">{analysis.resources.map((row, index) => <article key={`${row.kind}-${index}`}><h4>{resourceLabel(row.name, row.kind)}</h4><p>{row.is_active ? 'Restrição ativa' : 'Restrição não ativa'}{row.potential_bottleneck ? ' · Gargalo potencial' : ''}{!row.is_feasible ? ' · Violação' : ''}</p>
        {row.utilization_percent !== null && Number.isFinite(row.utilization_percent) ? <div className="result-utilization"><label htmlFor={`usage-${e.execution_id}-${index}`}>Utilização: {formatResource(row.utilization_percent)}%</label><progress id={`usage-${e.execution_id}-${index}`} max={100} value={Math.max(0, Math.min(100, row.utilization_percent))} />{row.utilization_percent > 100 && <small>O percentual ultrapassa a capacidade; a barra está limitada a 100%.</small>}</div> : <p>Utilização percentual: não se aplica.</p>}
        <dl><dt>LHS · valor calculado</dt><dd>{formatResource(row.lhs)}</dd><dt>RHS · limite ({row.operator === '<=' ? '≤' : row.operator === '>=' ? '≥' : '='})</dt><dd>{formatResource(row.rhs)}</dd><dt>Folga</dt><dd>{row.slack === null ? 'Não se aplica' : formatResource(row.slack)}</dd><dt>Excesso</dt><dd>{row.excess === null ? 'Não se aplica' : formatResource(row.excess)}</dd></dl>
      </article>)}</div></>}</section>}
    {!optimal && <p>A análise de utilização e folgas requer uma solução ótima; não há valores de decisão ótimos para apresentar nesta execução.</p>}
    <p className="result-timing">Tempo de execução: {formatResource(e.duration_ms)} ms</p>
    <details className="result-clone"><summary>Criar cenário a partir do modelo executado</summary>{e.snapshot_available ? scenarioId ? <p>Cenário #{scenarioId} criado. <Link to={`/problems/${e.problem_id}/scenarios`}>Abrir cenários</Link></p> : <><p>Cria uma cópia do snapshot da execução #{e.execution_id}, sem resolver novamente.</p><label>Nome do cenário<input value={scenarioName} maxLength={150} disabled={creating} onChange={event => setScenarioName(event.target.value)} /></label><button type="button" disabled={creating || !scenarioName.trim()} onClick={() => void clone()}>{creating ? 'Criando…' : 'Criar cenário'}</button>{scenarioError && <p role="alert">{scenarioError}</p>}</> : <p>O snapshot histórico está ausente ou inválido; não é possível criar um cenário fiel a esta execução.</p>}</details>
    <details ref={technical} className="result-technical"><summary>Detalhes técnicos</summary><p>Solver: SimplexDuasFases · {e.solver_version}</p><p>Iterações: fase I {e.iterations_phase1} · fase II {e.iterations_phase2}</p><p>Status original: {e.status}</p><p>Os parâmetros matemáticos desta análise pertencem à execução armazenada. Nenhuma consulta reexecuta o modelo.</p>{!variables && <><p>Resultados legados (os nomes vinculados podem refletir o cadastro atual):</p><ul>{e.variables.map(v => <li key={v.variable_id}>{v.variable_name}: {formatResource(v.value)}</li>)}</ul></>}{analysis && <ResourceTable data={analysis} />}</details>
  </section>;
}
