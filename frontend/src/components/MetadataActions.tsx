import { useState } from 'react';
import { editMetadata, deleteItem, duplicateScenario } from '../api/management';
import type { ManagedItem, ManagedKind } from '../api/management';
import './management.css';

function Editor({ kind, item, duplicate, onDone, onCancel }: {
  kind: ManagedKind; item: ManagedItem; duplicate: boolean; onDone: () => void; onCancel: () => void;
}) {
  const [name, setName] = useState(duplicate ? `${item.name.slice(0, 142)} (cópia)` : item.name);
  const [description, setDescription] = useState(item.description ?? '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  return <form className="metadata-editor" onSubmit={async event => {
    event.preventDefault();
    if (!name.trim()) { setError('Informe um nome.'); return; }
    setBusy(true); setError('');
    try {
      if (duplicate) await duplicateScenario(item.id, name.trim(), description.trim() || null);
      else await editMetadata(kind, item.id, name.trim(), description.trim() || null);
      onDone();
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Não foi possível salvar.'); }
    finally { setBusy(false); }
  }}>
    <h4>{duplicate ? 'Duplicar cenário' : 'Editar metadados'}</h4>
    <label>Nome<input required maxLength={150} value={name} onChange={e => setName(e.target.value)} disabled={busy} /></label>
    <label>Descrição<textarea value={description} onChange={e => setDescription(e.target.value)} disabled={busy} /></label>
    <p>{duplicate ? 'A cópia recebe o mesmo modelo matemático, sem execuções anteriores.' : 'Somente nome e descrição serão alterados. O modelo e suas execuções serão preservados.'}</p>
    {error && <p role="alert">{error}</p>}
    <button disabled={busy} type="submit">{busy ? 'Salvando…' : duplicate ? 'Criar cópia' : 'Salvar metadados'}</button>
    <button disabled={busy} type="button" onClick={onCancel}>Cancelar</button>
  </form>;
}

export default function MetadataActions({ kind, item, onChanged }: {
  kind: ManagedKind; item: ManagedItem; onChanged: () => void;
}) {
  const [mode, setMode] = useState<'edit' | 'delete' | 'duplicate' | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  return <div className="metadata-actions">
    {!mode && <><button type="button" onClick={() => { setMessage(''); setMode('edit'); }}>Editar metadados</button>
      {kind === 'scenarios' && <button type="button" onClick={() => { setMessage(''); setMode('duplicate'); }}>Duplicar cenário</button>}
      <button type="button" onClick={() => { setError(''); setMessage(''); setMode('delete'); }}>Excluir</button></>}
    {(mode === 'edit' || mode === 'duplicate') && <Editor kind={kind} item={item} duplicate={mode === 'duplicate'} onCancel={() => setMode(null)} onDone={() => { setMessage(mode === 'duplicate' ? 'Cópia criada.' : 'Metadados salvos.'); setMode(null); onChanged(); }} />}
    {mode === 'delete' && <section role="alertdialog" aria-label={`Confirmar exclusão de ${item.name}`}>
      <p>Excluir “{item.name}” (#{item.id})? Esta ação é permanente.{kind === 'problems' ? ' Todos os cenários, execuções, snapshots e resultados vinculados também serão excluídos.' : ' Todas as execuções, snapshots e resultados deste cenário também serão excluídos.'}</p>
      <p>Esta exclusão é definitiva e não pode ser desfeita. O histórico excluído não poderá ser consultado.</p>
      {error && <p role="alert">{error}</p>}
      <button type="button" disabled={busy} onClick={async () => {
        setBusy(true); setError('');
        try { await deleteItem(kind, item.id); setMode(null); onChanged(); }
        catch (reason) { setError(reason instanceof Error ? reason.message : 'Não foi possível excluir.'); }
        finally { setBusy(false); }
      }}>{busy ? 'Excluindo…' : 'Excluir definitivamente'}</button>
      <button type="button" disabled={busy} onClick={() => setMode(null)}>Cancelar</button>
    </section>}
    {message && <p role="status">{message}</p>}
  </div>;
}
