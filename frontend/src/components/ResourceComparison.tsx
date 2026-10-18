import { useEffect, useState } from 'react';
import { getResourceComparison } from '../api/resources';
import type { ScenarioComparison } from '../types/scenario';
import type { ResourceComparison as Comparison } from '../types/resources';
import ResourcePanel from './ResourceAnalysis';
import { formatResource, resourceLabel } from './resourceFormatting';

const transitions: Record<string, string> = {
  became_active: 'Tornou-se ativa', became_inactive: 'Deixou de ser ativa', unchanged: 'Sem mudança',
  became_potential: 'Novo potencial gargalo', ceased_potential: 'Deixou de ser potencial gargalo',
};

function ComparisonResult({ problemId, baseline, target }: {
  problemId: number; baseline: ScenarioComparison; target: ScenarioComparison;
}) {
  const [data, setData] = useState<Comparison | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    getResourceComparison(problemId, baseline, target, controller.signal)
      .then(value => { if (!controller.signal.aborted) setData(value); })
      .catch(reason => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Não foi possível comparar os recursos.'); });
    return () => controller.abort();
  }, [problemId, baseline, target]);
  if (error) return <p role="alert">Comparação indisponível: {error}</p>;
  if (!data) return <p role="status">Comparando recursos…</p>;
  return <>
    <p>Referência: {baseline.scenario_name}, execução #{data.baseline.execution_id}. Comparado: {target.scenario_name}, execução #{data.target.execution_id}.</p>
    {data.objective_comparable ? <p>Variação do objetivo: {formatResource(data.objective_delta)} ({data.objective_delta_percent == null ? 'percentual não aplicável' : `${formatResource(data.objective_delta_percent)}%`}). Melhoria: {formatResource(data.objective_improvement)} — valores positivos indicam melhora.</p>
      : <p>Objetivos não comparáveis: {data.objective_reason}</p>}
    <p>Diferenças = comparado − referência. Utilização em pontos percentuais (p.p.).</p>
    <div className="resource-scroll" tabIndex={0} role="region" aria-label="Diferenças de recursos">
      <table><caption>Variações por recurso</caption><thead><tr>{['Recurso', 'Δ LHS', 'Δ RHS', 'Δ Folga', 'Δ Excesso', 'Δ Utilização (p.p.)', 'Atividade', 'Gargalo potencial'].map(h => <th scope="col" key={h}>{h}</th>)}</tr></thead>
        <tbody>{data.resources.map((row, index) => <tr key={`${row.kind}-${row.name}-${index}`}>
          <th scope="row">{resourceLabel(row.name, row.kind)}</th>
          {!row.comparable ? <td colSpan={7}>{row.reason ?? 'Recurso não comparável.'}</td> : <>
            <td>{formatResource(row.lhs_delta)}</td><td>{formatResource(row.rhs_delta)}</td>
            <td>{formatResource(row.slack_delta)}</td><td>{formatResource(row.excess_delta)}</td>
            <td>{formatResource(row.utilization_delta_pp)}</td>
            <td>{transitions[row.activity_change ?? ''] ?? 'Não se aplica'}</td>
            <td>{transitions[row.bottleneck_change ?? ''] ?? 'Não se aplica'}</td>
          </>}
        </tr>)}</tbody></table>
    </div>
    <h3>Recursos da referência</h3><ResourcePanel executionId={data.baseline.execution_id} scenarioId={baseline.scenario_id} />
    <h3>Recursos do cenário comparado</h3><ResourcePanel executionId={data.target.execution_id} scenarioId={target.scenario_id} />
  </>;
}

export default function ResourceComparison({ problemId, scenarios }: { problemId: number; scenarios: ScenarioComparison[] }) {
  const [baselineId, setBaselineId] = useState(String(scenarios[0]?.scenario_id ?? ''));
  const [targetId, setTargetId] = useState(String(scenarios[1]?.scenario_id ?? ''));
  const [retry, setRetry] = useState(0);
  const baseline = scenarios.find(s => String(s.scenario_id) === baselineId);
  const target = scenarios.find(s => String(s.scenario_id) === targetId);
  return <section className="resource-panel"><h2>Comparação de recursos</h2>
    <p>Compare consumo, limites e folgas. Restrições ativas são apenas possíveis gargalos.</p>
    {scenarios.length < 2 ? <p>Execute pelo menos dois cenários para comparar recursos.</p> : <>
      <div className="resource-selectors">
        <label>Cenário de referência<select value={baselineId} onChange={e => setBaselineId(e.target.value)}>{scenarios.map(s => <option key={s.scenario_id} value={s.scenario_id}>{s.scenario_name} · execução #{s.execution_id}</option>)}</select></label>
        <label>Cenário comparado<select value={targetId} onChange={e => setTargetId(e.target.value)}>{scenarios.map(s => <option key={s.scenario_id} value={s.scenario_id}>{s.scenario_name} · execução #{s.execution_id}</option>)}</select></label>
      </div>
      {baseline && target && baseline.scenario_id !== target.scenario_id ? <>
        <button type="button" onClick={() => setRetry(retry + 1)}>Recarregar comparação de recursos</button>
        <ComparisonResult key={`${baseline.execution_id}-${target.execution_id}-${retry}`} problemId={problemId} baseline={baseline} target={target} />
      </> : <p>Selecione dois cenários diferentes.</p>}
    </>}
  </section>;
}
