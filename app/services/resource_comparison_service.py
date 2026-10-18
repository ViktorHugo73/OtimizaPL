"""Compare persisted executions without solving or changing the mathematical engine."""
from math import isfinite

from app.schemas.resource_comparison import ResourceComparisonResponse, ResourceDifference
from app.services.resource_analysis_service import analyze_execution


def difference(target, baseline):
    if target is None or baseline is None:
        return None
    result = target - baseline
    if not isfinite(result):
        raise ValueError('Diferença numérica não finita.')
    return result


def indexed(rows):
    result = {}
    for row in rows:
        key = (row.kind, row.name)
        if key in result:
            raise ValueError('Nomes de restrições duplicados impedem comparação inequívoca.')
        result[key] = row
    return result


def compare_executions(baseline_execution, target_execution):
    if baseline_execution.problem_id != target_execution.problem_id:
        raise ValueError('Execuções devem pertencer ao mesmo problema.')
    baseline = analyze_execution(baseline_execution)
    target = analyze_execution(target_execution)
    if not baseline.is_feasible or not target.is_feasible:
        raise ValueError('Comparação requer duas soluções factíveis.')
    left, right = indexed(baseline.resources), indexed(target.resources)
    rows = []
    for kind, name in dict.fromkeys([*left, *right]):
        a, b = left.get((kind, name)), right.get((kind, name))
        comparable = a is not None and b is not None and a.operator == b.operator
        row = ResourceDifference(name=name, kind=kind, baseline=a, target=b,
                                 comparable=comparable,
                                 reason=None if comparable else 'Restrição ausente ou operador alterado.')
        if comparable:
            for field in ('lhs', 'rhs', 'slack', 'excess'):
                setattr(row, field + '_delta', difference(getattr(b, field), getattr(a, field)))
            row.utilization_delta_pp = difference(b.utilization_percent, a.utilization_percent)
            row.activity_change = ('unchanged' if a.is_active == b.is_active else
                                   'became_active' if b.is_active else 'became_inactive')
            row.bottleneck_change = ('unchanged' if a.potential_bottleneck == b.potential_bottleneck else
                                     'became_potential' if b.potential_bottleneck else 'ceased_potential')
        rows.append(row)
    try:
        a_model = baseline_execution.analysis_snapshot['model']
        b_model = target_execution.analysis_snapshot['model']
        a_objective = {v['name']: float(v['objective_coefficient']) for v in a_model['variables']}
        b_objective = {v['name']: float(v['objective_coefficient']) for v in b_model['variables']}
        sense = a_model['objective_type']
        comparable = (sense in ('min', 'max') and sense == b_model['objective_type']
                      and a_objective == b_objective
                      and all(isfinite(v) for v in [*a_objective.values(), *b_objective.values()]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('Função objetivo inválida no snapshot.') from exc
    delta = difference(target.objective_value, baseline.objective_value) if comparable else None
    comparable = comparable and delta is not None
    percent = None
    if comparable and baseline.objective_value != 0:
        percent = delta / abs(baseline.objective_value) * 100
        if not isfinite(percent):
            percent = None
    return ResourceComparisonResponse(
        problem_id=baseline.problem_id, baseline=baseline, target=target,
        objective_comparable=comparable,
        objective_reason=None if comparable else 'Função objetivo alterada ou valor indisponível.',
        objective_delta=delta, objective_delta_percent=percent,
        objective_improvement=(-delta if sense == 'min' else delta) if comparable else None,
        resources=rows,
    )
