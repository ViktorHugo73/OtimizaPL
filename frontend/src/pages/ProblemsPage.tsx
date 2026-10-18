import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listProblems } from '../api/management';
import type { ProblemSummary } from '../api/management';
import MetadataActions from '../components/MetadataActions';

function ProblemList({ onChanged }: { onChanged: () => void }) {
  const [items, setItems] = useState<ProblemSummary[] | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    listProblems(controller.signal).then(data => { if (!controller.signal.aborted) setItems(data); })
      .catch(reason => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Falha ao consultar problemas.'); });
    return () => controller.abort();
  }, []);
  if (error) return <p role="alert">{error}</p>;
  if (!items) return <p role="status">Carregando problemas…</p>;
  if (!items.length) return <p>Nenhum problema cadastrado. Use “Novo problema” para começar.</p>;
  return <>{items.map(item => <article key={item.id}><h2>{item.name}</h2>
    <p>#{item.id} · {item.objective_type === 'min' ? 'Minimização' : 'Maximização'}</p>
    <p>{item.description || 'Sem descrição.'}</p>
    <nav><Link to={`/problems/${item.id}`}>Abrir problema</Link><Link to={`/problems/${item.id}/scenarios`}>Cenários</Link><Link to={`/problems/${item.id}/executions`}>Histórico</Link></nav>
    <MetadataActions kind="problems" item={item} onChanged={onChanged} />
  </article>)}</>;
}

export default function ProblemsPage() {
  const [refresh, setRefresh] = useState(0);
  return <main className="problem-list"><h1>Problemas cadastrados</h1>
    <nav><Link to="/problems/new">Novo problema</Link><button type="button" onClick={() => setRefresh(refresh + 1)}>Atualizar lista</button></nav>
    <ProblemList key={refresh} onChanged={() => setRefresh(refresh + 1)} />
  </main>;
}
