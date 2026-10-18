import type { ReactNode } from 'react';

export default function ProblemField({ id, label, error, hint, children }: { id: string; label: string; error?: string; hint?: string; children: (props: { id: string; 'aria-invalid': boolean; 'aria-describedby': string | undefined }) => ReactNode }) {
  return <div className="wizard-field">
    <label htmlFor={id}>{label}</label>
    {children({ id, 'aria-invalid': Boolean(error), 'aria-describedby': error ? `${id}-error` : hint ? `${id}-hint` : undefined })}
    {error ? <p className="wizard-field-error" id={`${id}-error`}>{error}</p> : hint && <p className="wizard-hint" id={`${id}-hint`}>{hint}</p>}
  </div>;
}
