import ExecutionResult from '../components/ExecutionResult';
import { statusLabel } from '../components/executionFormatting';
import { useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { getExecutionHistory } from '../api/executions';
import type { ExecutionHistoryItem } from '../api/executions';



import { formatResource } from '../components/resourceFormatting';
import './executionHistory.css';

function dateLabel(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Data indisponível' : date.toLocaleString('pt-BR', { timeZoneName: 'short' });
}

function HistoryContent({ problemId }: { problemId: number }) {
  const [items, setItems] = useState<ExecutionHistoryItem[] | null>(null);
  const [error, setError] = useState('');
  const [search, setSearch] = useSearchParams();
  useEffect(() => {
    const controller = new AbortController();
    getExecutionHistory(problemId, controller.signal)
      .then(value => {
        if (!controller.signal.aborted) setItems([...value].sort((a, b) =>
          Date.parse(b.created_at) - Date.parse(a.created_at) || b.execution_id - a.execution_id));
      })
      .catch(reason => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Falha ao carregar o histórico.'); });
    return () => controller.abort();
  }, [problemId]);
  if (error) return <p role="alert">{error}</p>;
  if (!items) return <p role="status">Carregando execuções anteriores…</p>;
  if (!items.length) return <p>Nenhuma execução registrada. Resolva o problema ou um cenário para criar uma execução.</p>;
  const requestedId = search.get('execution');
  const selected = items.find(item => String(item.execution_id) === requestedId);
  return <>
    {selected && <ExecutionResult key={selected.execution_id} execution={selected} />}
    <details open={!selected}><summary>Consultar histórico</summary>
    <p>{items.length} execuções · mais recentes primeiro. Datas no fuso horário do navegador.</p>
    <div className="resource-scroll" tabIndex={0} role="region" aria-label="Histórico de execuções">
      <table><caption>Execuções anteriores do problema #{problemId}</caption>
        <thead><tr>{['Execução', 'Data e hora', 'Solver', 'Status', 'Objetivo', 'Variáveis', 'Tempo (ms)', 'Detalhes'].map(h => <th key={h} scope="col">{h}</th>)}</tr></thead>
        <tbody>{items.map(item => <tr key={item.execution_id} aria-selected={selected?.execution_id === item.execution_id}>
          <th scope="row">#{item.execution_id}</th><td>{dateLabel(item.created_at)}</td><td>SimplexDuasFases {item.solver_version}</td><td>{statusLabel(item.status)}</td>
          <td>{item.objective_value === null ? 'Indisponível' : formatResource(item.objective_value)}</td>
          <td>{item.recorded_variables ? item.recorded_variables.map(v => `${v.name} = ${formatResource(v.value)}`).join('; ') : 'Snapshot indisponível; consultar detalhes'}</td>
          <td>{formatResource(item.duration_ms)}</td><td><Link to={`?execution=${item.execution_id}`} aria-current={selected?.execution_id === item.execution_id ? 'true' : undefined}>Abrir execução #{item.execution_id}</Link></td>
        </tr>)}</tbody>
      </table>
    </div>
    </details>
    {requestedId && !selected && <p role="alert">Execução não encontrada neste problema.</p>}
    {selected ? <><button type="button" onClick={() => setSearch({})}>Fechar detalhes</button></> : <p>Selecione “Abrir execução” para consultar seus dados e sua análise.</p>}
  </>;
}

export default function ExecutionHistoryPage() {
  const { problemId } = useParams();
  const id = Number(problemId);
  const [refresh, setRefresh] = useState(0);
  if (!Number.isInteger(id) || id <= 0) return <main><p role="alert">Identificador do problema inválido.</p></main>;
  return <main className="execution-history"><h1>Histórico de execuções</h1>
    <nav><Link to={`/problems/${id}`}>Voltar ao problema</Link> · <Link to={`/problems/${id}/scenarios`}>Cenários</Link> · <Link to={`/problems/${id}/comparison`}>Comparação</Link></nav>
    <button type="button" onClick={() => setRefresh(refresh + 1)}>Atualizar histórico</button>
    <HistoryContent key={`${id}-${refresh}`} problemId={id} />
  </main>;
}
