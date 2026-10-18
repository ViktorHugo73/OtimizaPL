import { useEffect, useState } from 'react';
import { getExecutionResources } from '../api/resources';
import type { ScenarioComparison } from '../types/scenario';
import type { ResourceAnalysis } from '../types/resources';
import { formatResource } from './resourceFormatting';
import { chartScale } from './chartData';
import './comparisonCharts.css';

type Row = { label: string; value: number | null; reason?: string };
type Loaded = { data?: ResourceAnalysis; error?: string };

function Bars({ title, rows, percent = false }: { title: string; rows: Row[]; percent?: boolean }) {
  const scale = chartScale(rows.map(r => r.value), percent ? 100 : 0);
  return <figure className="comparison-chart"><figcaption>{title}</figcaption>
    <div className="chart-axis" aria-hidden="true"><span>{formatResource(scale.min)}{percent ? '%' : ''}</span><span>{formatResource(scale.max)}{percent ? '%' : ''}</span></div>
    <ul>{rows.map((row, index) => <li key={row.label}>
      <span className="chart-label">{row.label}</span>
      <div className="chart-track" aria-hidden="true">
        <span className="chart-zero" style={{ left: `${scale.zero}%` }} />
        {row.value !== null && <span className={`chart-bar chart-color-${index % 4}`} style={{ left: `${scale.bar(row.value).left}%`, width: `${scale.bar(row.value).width}%` }} />}
      </div>
      <span className="chart-value">{row.value === null ? row.reason ?? 'Não se aplica' : `${formatResource(row.value)}${percent ? '%' : ''}`}</span>
    </li>)}</ul>
    {!rows.length && <p>Nenhum cenário disponível.</p>}
  </figure>;
}

export default function ComparisonCharts({ scenarios }: { scenarios: ScenarioComparison[] }) {
  const [loaded, setLoaded] = useState<Record<number, Loaded>>({});
  const [variable, setVariable] = useState('');
  const [resource, setResource] = useState('');
  const [slack, setSlack] = useState('');
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    for (const scenario of scenarios) {
      if (scenario.status !== 'optimal') continue;
      getExecutionResources(scenario.execution_id, controller.signal)
        .then(data => { if (!controller.signal.aborted) setLoaded(previous => ({ ...previous, [scenario.execution_id]: { data } })); })
        .catch(error => { if (!controller.signal.aborted) setLoaded(previous => ({ ...previous, [scenario.execution_id]: { error: error instanceof Error ? error.message : 'Falha na consulta' } })); });
    }
    return () => controller.abort();
  }, [scenarios, retry]);
  const variables = [...new Set(scenarios.flatMap(s => Object.keys(s.variables)))];
  const constraints = [...new Set(Object.values(loaded).flatMap(entry => entry.data?.resources.filter(r => r.kind === 'constraint').map(r => r.name) ?? []))];
  const selectedVariable = variables.includes(variable) ? variable : variables[0] ?? '';
  const defaultMetric = (metric: 'slack' | 'utilization_percent') => constraints.find(name => Object.values(loaded).some(entry => entry.data?.resources.some(r => r.kind === 'constraint' && r.name === name && r[metric] !== null))) ?? constraints[0] ?? '';
  const selectedResource = constraints.includes(resource) ? resource : defaultMetric('utilization_percent');
  const selectedSlack = constraints.includes(slack) ? slack : defaultMetric('slack');
  const label = (s: ScenarioComparison) => `${s.scenario_name} · #${s.execution_id}`;
  const resourceRows = (name: string, metric: 'slack' | 'utilization_percent'): Row[] => scenarios.map(s => {
    if (s.status !== 'optimal') return { label: label(s), value: null, reason: `Indisponível (${s.status})` };
    const entry = loaded[s.execution_id];
    if (!entry) return { label: label(s), value: null, reason: 'Carregando…' };
    if (entry.error) return { label: label(s), value: null, reason: 'Análise indisponível' };
    const matches = entry.data?.resources.filter(r => r.kind === 'constraint' && r.name === name) ?? [];
    if (matches.length !== 1) return { label: label(s), value: null, reason: matches.length ? 'Nome ambíguo' : 'Restrição ausente' };
    return { label: label(s), value: matches[0][metric] };
  });
  const selector = (title: string, value: string, options: string[], change: (value: string) => void) =>
    <label className="chart-selector">{title}<select value={value} disabled={!options.length} onChange={e => change(e.target.value)}>
      {!options.length && <option value="">Nenhum dado disponível</option>}
      {options.map(name => <option key={name} value={name}>{name}</option>)}
    </select></label>;
  return <section className="comparison-charts" aria-label="Gráficos comparativos"><h2>Gráficos comparativos</h2>
    <p>Os rótulos identificam a execução. Cada gráfico usa uma escala comum entre cenários; recursos e variáveis são comparados individualmente para evitar misturar unidades.</p>
    <p>Valores do objetivo são descritivos: se os coeficientes ou o sentido mudaram, uma barra menor não significa necessariamente melhoria.</p>
    <div className="chart-grid">
      <Bars title="Função objetivo por cenário" rows={scenarios.map(s => ({ label: label(s), value: s.status === 'optimal' ? s.objective_value : null, reason: `Indisponível (${s.status})` }))} />
      <div>{selector('Variável', selectedVariable, variables, setVariable)}<Bars title={`Valores da variável ${selectedVariable}`} rows={scenarios.map(s => ({ label: label(s), value: s.status === 'optimal' ? s.variables[selectedVariable] ?? null : null, reason: 'Valor indisponível' }))} /></div>
      <div>{selector('Recurso para utilização', selectedResource, constraints, setResource)}<Bars title={`Utilização — ${selectedResource || 'recursos'}`} rows={resourceRows(selectedResource, 'utilization_percent')} percent /></div>
      <div>{selector('Restrição para folga', selectedSlack, constraints, setSlack)}<Bars title={`Folga — ${selectedSlack || 'restrições'}`} rows={resourceRows(selectedSlack, 'slack')} /><p>Folga = RHS − LHS para restrições ≤. Igualdades e restrições ≥ não possuem folga; seu excesso está na análise detalhada.</p></div>
    </div>
    {scenarios.some(s => loaded[s.execution_id]?.error) && <div role="status"><p>Algumas análises não puderam ser carregadas:</p><ul>{scenarios.filter(s => loaded[s.execution_id]?.error).map(s => <li key={s.execution_id}>{label(s)}: {loaded[s.execution_id].error}</li>)}</ul><button type="button" onClick={() => { setLoaded({}); setRetry(retry + 1); }}>Tentar carregar novamente</button></div>}
  </section>;
}
