import { useEffect, useState } from 'react';
import { getExecutionResources, getScenarioResources } from '../api/resources';
import type { ResourceAnalysis as Analysis } from '../types/resources';
import './resources.css';

import { formatResource, resourceLabel } from "./resourceFormatting";

export function ResourceTable({ data }: { data: Analysis }) {
  return <div className="resource-analysis">
    <p>Execução #{data.execution_id} · {data.is_feasible ? 'Solução factível' : 'Solução com violações'}</p>
    <p className="resource-note">LHS é o valor calculado; RHS é o limite da restrição. Um gargalo potencial não garante melhoria ao ampliar o recurso.</p>
    {!data.resources.length ? <p>Nenhum recurso para analisar.</p> :
      <div className="resource-scroll" tabIndex={0} role="region" aria-label="Tabela de recursos">
        <table><caption>Análise de recursos da execução #{data.execution_id}</caption>
          <thead><tr>{['Recurso', 'Operador', 'LHS', 'RHS', 'Folga', 'Excesso', 'Utilização', 'Ativa', 'Gargalo potencial'].map(h => <th scope="col" key={h}>{h}</th>)}</tr></thead>
          <tbody>{data.resources.map((row, index) => <tr key={`${row.kind}-${row.name}-${index}`}>
            <th scope="row">{resourceLabel(row.name, row.kind)}{!row.is_feasible && <span className="resource-badge">Violação</span>}</th>
            <td>{row.operator}</td><td>{formatResource(row.lhs)}</td><td>{formatResource(row.rhs)}</td>
            <td>{formatResource(row.slack)}</td><td>{formatResource(row.excess)}</td>
            <td>{row.utilization_percent == null ? 'Não se aplica' : `${formatResource(row.utilization_percent)}%`}</td>
            <td>{row.is_active ? 'Sim' : 'Não'}</td>
            <td>{row.potential_bottleneck ? <span className="resource-badge">Potencial</span> : 'Não'}</td>
          </tr>)}</tbody>
        </table>
      </div>}
  </div>;
}

function ResourceLoader({ executionId, scenarioId }: { executionId?: number; scenarioId: number }) {
  const [data, setData] = useState<Analysis | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    const request = executionId ? getExecutionResources(executionId, controller.signal)
      : getScenarioResources(scenarioId, controller.signal);
    request.then(value => { if (!controller.signal.aborted) setData(value); })
      .catch(reason => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Não foi possível carregar os recursos.'); });
    return () => controller.abort();
  }, [executionId, scenarioId]);
  if (error) return <p role="alert">Análise indisponível: {error}</p>;
  if (!data) return <p role="status">Carregando análise de recursos…</p>;
  return <ResourceTable data={data} />;
}

export default function ResourcePanel({ executionId, scenarioId }: { executionId?: number; scenarioId: number }) {
  const [open, setOpen] = useState(false);
  const [retry, setRetry] = useState(0);
  return <section className="resource-panel" aria-label="Análise de recursos">
    <button type="button" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? 'Ocultar recursos' : 'Analisar recursos'}</button>
    {open && <><button type="button" onClick={() => setRetry(retry + 1)}>Atualizar análise</button>
      <ResourceLoader key={`${scenarioId}-${executionId}-${retry}`} executionId={executionId} scenarioId={scenarioId} /></>}
  </section>;
}
