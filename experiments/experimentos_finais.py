"""Reproducible final experiments. Does not modify the solver or application DB."""
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter_ns

import numpy as np
import scipy
from experiments.gerador import (ProblemaGerado, gerar_factivel_limitado,
    gerar_factivel_misto, gerar_inviavel, gerar_ilimitado)
from models.artigo_v1_0 import carregar_modelo_artigo_v1_0
from models.mix_producao import carregar_modelo_mix
from motor import SimplexDuasFases, VERSION
from validacao import resolver_highs
from validacao.factibilidade import avaliar_factibilidade

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'factivel_limitado': 'optimal', 'factivel_misto': 'optimal',
            'inviavel': 'infeasible', 'ilimitado': 'unbounded', 'aplicacao': 'optimal'}


def generate_cases(scale_instances=10):
    cases = []
    # Same 100 seeded instances as benchmark v2, including regression P045.
    for i in range(35):
        k = i + 1
        cases.append(('classes', gerar_factivel_limitado(f'P{k:03}', 2+i%10, 3+i%15,
                      3471+k, 'min' if k%2 == 0 else 'max')))
    for i in range(35):
        k = i + 36
        cases.append(('classes', gerar_factivel_misto(f'P{k:03}', 2+i%8, 3+i%12,
                      7000+k, 'min' if k%2 == 0 else 'max')))
    for i in range(15):
        k = i + 71
        cases.append(('classes', gerar_inviavel(f'P{k:03}', 2+i%10, 10000+k)))
    for i in range(15):
        k = i + 86
        cases.append(('classes', gerar_ilimitado(f'P{k:03}', 2+i%10, 13000+k)))
    k = 0
    for n in [5, 10, 20, 50, 100]:
        for _ in range(scale_instances):
            k += 1
            cases.append(('escala', gerar_factivel_limitado(f'ESC{k:03}', n, 2*n,
                          20000+k, 'min' if k%2 == 0 else 'max')))
    for identifier, model in [('FEIXES', carregar_modelo_artigo_v1_0()), ('MIX', carregar_modelo_mix())]:
        cases.append(('aplicacao', ProblemaGerado(identifier, 'aplicacao', model['A'],
            model['b'], model['c'], model['operadores'], model['objetivo'], 0,
            len(model['c']), len(model['b']))))
    return cases


def evaluate(problem, own, reference):
    result = {'status_proprio': own.status, 'status_highs': reference.status,
              'status_esperado': EXPECTED[problem.classe], 'erro_absoluto': None,
              'erro_relativo': None, 'erro_normalizado': None,
              'violacao_proprio': None, 'violacao_highs': None,
              'objetivo_proprio': None, 'objetivo_highs': None}
    approved = own.status == reference.status == result['status_esperado']
    if own.status == reference.status == 'optimal':
        finite = (own.x is not None and reference.x is not None
                  and np.all(np.isfinite(own.x)) and np.all(np.isfinite(reference.x))
                  and own.valor_objetivo is not None and reference.valor_objetivo is not None
                  and np.isfinite(own.valor_objetivo) and np.isfinite(reference.valor_objetivo))
        if not finite:
            result['aprovado'] = False
            return result
        own_feas = avaliar_factibilidade(problem.A, problem.b, problem.operadores, own.x)
        ref_feas = avaliar_factibilidade(problem.A, problem.b, problem.operadores, reference.x)
        difference = abs(own.valor_objetivo - reference.valor_objetivo)
        normalized = difference / max(1, abs(reference.valor_objetivo))
        result.update(objetivo_proprio=float(own.valor_objetivo), objetivo_highs=float(reference.valor_objetivo),
                      erro_absoluto=float(difference), erro_normalizado=float(normalized),
                      erro_relativo=float(difference/abs(reference.valor_objetivo)) if reference.valor_objetivo != 0 else None,
                      violacao_proprio=own_feas.violacao_maxima, violacao_highs=ref_feas.violacao_maxima)
        approved = approved and own_feas.factivel and ref_feas.factivel and normalized <= 1e-7
    result['aprovado'] = bool(approved)
    return result


def measure(problem, repetitions):
    args = (problem.A, problem.b, problem.c, problem.operadores, problem.objetivo)
    # One warm-up per solver and instance, excluded from timing.
    SimplexDuasFases().resolver(*args)
    resolver_highs(*args)
    samples = []
    for repetition in range(repetitions):
        solvers = {'proprio': SimplexDuasFases().resolver, 'highs': resolver_highs}
        results, times = {}, {}
        order = ['proprio', 'highs'] if repetition % 2 == 0 else ['highs', 'proprio']
        for name in order:
            start = perf_counter_ns()
            results[name] = solvers[name](*args)
            times[name] = (perf_counter_ns() - start) / 1e6
        own, reference = results['proprio'], results['highs']
        sample = evaluate(problem, own, reference)
        sample.update(repeticao=repetition+1, ordem=','.join(order),
                      tempo_proprio_ms=times['proprio'], tempo_highs_ms=times['highs'],
                      iteracoes_fase1=own.iteracoes_fase1, iteracoes_fase2=own.iteracoes_fase2,
                      iteracoes_highs=reference.iteracoes)
        samples.append(sample)
    summary = dict(samples[-1])
    for key in ('repeticao', 'ordem'):
        summary.pop(key)
    for key in ('tempo_proprio_ms', 'tempo_highs_ms', 'iteracoes_fase1', 'iteracoes_fase2', 'iteracoes_highs'):
        values = [s[key] for s in samples if s[key] is not None]
        summary[key] = median(values) if values else None
    for key in ('erro_absoluto', 'erro_relativo', 'erro_normalizado', 'violacao_proprio', 'violacao_highs'):
        values = [s[key] for s in samples if s[key] is not None]
        summary[key] = max(values) if values else None
    summary['aprovado'] = all(s['aprovado'] for s in samples)
    summary['status_estavel'] = len({(s['status_proprio'], s['status_highs']) for s in samples}) == 1
    summary['aprovado'] &= summary['status_estavel']
    return summary, samples


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def report(rows, output):
    approved = sum(r['aprovado'] for r in rows)
    lines = ['# Experimentos finais — resultados medidos', '',
             f'Instâncias aprovadas: **{approved}/{len(rows)}**.', '',
             '## Por classe', '', '| Grupo/classe | Casos | Aprovados |', '|---|---:|---:|']
    groups = defaultdict(list)
    for row in rows:
        groups[(row['grupo'], row['classe'])].append(row)
    for (group, kind), values in groups.items():
        lines.append(f'| {group}/{kind} | {len(values)} | {sum(v["aprovado"] for v in values)} |')
    lines += ['', '## Comportamento por tamanho', '',
              'Tempos: mediana entre instâncias das medianas de cada execução. Iterações: medianas entre instâncias.', '',
              '| Variáveis | Restrições reais | Casos | Próprio (ms) | HiGHS (ms) | Fase I | Fase II | HiGHS nit |',
              '|---:|---:|---:|---:|---:|---:|---:|---:|']
    for n in sorted({r['n_variaveis'] for r in rows if r['grupo'] == 'escala'}):
        values = [r for r in rows if r['grupo'] == 'escala' and r['n_variaveis'] == n and 'tempo_proprio_ms' in r]
        if not values:
            continue
        cols = []
        for key in ('tempo_proprio_ms', 'tempo_highs_ms', 'iteracoes_fase1', 'iteracoes_fase2', 'iteracoes_highs'):
            nums = [r[key] for r in values if r[key] is not None]
            cols.append(f'{median(nums):.6g}' if nums else 'N/A')
        lines.append(f'| {n} | {values[0]["n_restricoes"]} | {len(values)} | ' + ' | '.join(cols) + ' |')
    errors = [r['erro_normalizado'] for r in rows if r.get('erro_normalizado') is not None]
    relative = [r['erro_relativo'] for r in rows if r.get('erro_relativo') is not None]
    lines += ['', f'Maior erro normalizado: {max(errors, default=0):.12g}.',
              f'Maior erro relativo convencional (referência não nula): {max(relative, default=0):.12g}.', '',
              '## Metodologia e limites', '',
              '- Erro relativo = |Z próprio − Z HiGHS| / |Z HiGHS|; nulo se a referência é zero.',
              '- Erro normalizado = |diferença| / max(1, |Z HiGHS|); aprovação exige ≤ 1e-7 e factibilidade dos dois vetores com tolerância absoluta 1e-7.',
              '- Inviáveis e ilimitados não possuem erro de objetivo definido: campos vazios, nunca zero artificial.',
              '- Aprovação exige status esperado pela construção e aprovação em todas as repetições. Exceções são registradas como falhas.',
              '- Um aquecimento por instância/solver; ordem alternada, cinco repetições por padrão; preparação do solver e escrita de arquivos fora do cronômetro.',
              '- Tempos incluem conversão de entradas e adaptadores, mas excluem HTTP, interface, banco e geração. Medem os solvers via suas interfaces Python.',
              '- HiGHS usa scipy.optimize.linprog(method="highs") com presolve e escolhas automáticas padrão. nit não é diretamente equivalente às iterações do Simplex em duas fases.',
              '- Tamanhos reais incluem n limites superiores: 2n linhas aleatórias + n limites, total 3n. Escala cobre apenas a família factível limitada; não generalizar a todas as classes.',
              '- Resultados de tempo são locais, sujeitos a carga do sistema e bibliotecas. Não representam superioridade universal de um algoritmo.',
              '- Feixes: modelo reconstruído com coeficientes inferidos. Mix: caso sintético. Instâncias, sementes, amostras e ambiente acompanham o relatório.', '', '## Falhas', '']
    failures = [r for r in rows if not r['aprovado']]
    lines += [f'- {r["id"]}: {r.get("exception", str((r.get("status_proprio"), r.get("status_highs"))))}' for r in failures] or ['Nenhuma falha nesta execução.']
    (output / 'relatorio.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repetitions', type=int, default=5)
    parser.add_argument('--scale-instances', type=int, default=10)
    options = parser.parse_args()
    if options.repetitions < 1 or options.scale_instances < 1:
        parser.error('Repetições e instâncias devem ser positivas.')
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / 'instances').mkdir()
    sources = ['motor/simplex.py', 'motor/version.py', 'validacao/highs.py',
               'validacao/factibilidade.py', 'experiments/gerador.py', 'experiments/experimentos_finais.py']
    environment = dict(started_at=datetime.now(timezone.utc).isoformat(), python=sys.version,
        platform=platform.platform(), processor=platform.processor(), cpu_count=os.cpu_count(),
        numpy=np.__version__, scipy=scipy.__version__, solver_version=VERSION,
        repetitions=options.repetitions, warmups=1, scale_instances=options.scale_instances,
        thread_environment={name: os.environ.get(name) for name in ['OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS']},
        hashes={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources})
    (output / 'ambiente.json').write_text(json.dumps(environment, indent=2), encoding='utf-8')
    rows, raw = [], []
    for group, problem in generate_cases(options.scale_instances):
        (output / 'instances' / f'{problem.id}.json').write_text(json.dumps(problem.para_dict(), indent=2), encoding='utf-8')
        identity = dict(id=problem.id, grupo=group, classe=problem.classe, seed=problem.seed,
                        n_variaveis=problem.n_variaveis, n_restricoes=len(problem.b), objetivo=problem.objetivo)
        try:
            result, samples = measure(problem, options.repetitions)
            rows.append({**identity, **result})
            raw.extend({**identity, **sample} for sample in samples)
        except Exception as exc:
            rows.append({**identity, 'aprovado': False, 'exception': f'{type(exc).__name__}: {exc}'})
        write_csv(output / 'resultados.csv', rows)
        write_csv(output / 'amostras.csv', raw)
        print(f'{problem.id} {problem.n_variaveis}x{len(problem.b)} aprovado={rows[-1]["aprovado"]}', flush=True)
    report(rows, output)
    environment['finished_at'] = datetime.now(timezone.utc).isoformat()
    environment['total'] = len(rows)
    environment['approved'] = sum(r['aprovado'] for r in rows)
    (output / 'ambiente.json').write_text(json.dumps(environment, indent=2), encoding='utf-8')
    print(f'Resultado: {environment["approved"]}/{len(rows)}. {output}', flush=True)
    return 0 if all(r['aprovado'] for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
