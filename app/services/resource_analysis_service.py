"""Resource diagnostics from immutable execution snapshots; no solver calls."""
from math import isfinite

from app.schemas.resource_analysis import ConstraintResourceAnalysis, ResourceAnalysisResponse

ABS_TOLERANCE = 1e-7
REL_TOLERANCE = 1e-9


def _finite(value):
    if isinstance(value, bool):
        raise ValueError('Valor numérico inválido.')
    result = float(value)
    if not isfinite(result):
        raise ValueError('Valor numérico não finito.')
    return result


def analyze_resources(snapshot, values):
    """Analyze constraints and variable bounds without modifying inputs."""
    try:
        variables = snapshot['variables']
        names = [v['name'] for v in variables]
        if not names or len(set(names)) != len(names) or set(values) != set(names):
            raise ValueError('Variáveis da solução incompatíveis com o snapshot.')
        solution = {name: _finite(values[name]) for name in names}
        rows = []

        def append(name, kind, operator, rhs, coefficients):
            if operator not in ('<=', '>=', '=') or not set(coefficients).issubset(solution):
                raise ValueError('Restrição inválida no snapshot.')
            rhs = _finite(rhs)
            coefficients = {key: _finite(val) for key, val in coefficients.items()}
            lhs = _finite(sum(coef * solution[key] for key, coef in coefficients.items()))
            residual = _finite(lhs - rhs)
            tolerance = ABS_TOLERANCE + REL_TOLERANCE * max(abs(lhs), abs(rhs))
            violation = max(residual, 0.0) if operator == '<=' else max(-residual, 0.0) if operator == '>=' else abs(residual)
            active = abs(residual) <= tolerance
            utilization = None
            if (operator == '<=' and rhs > 0
                    and any(c > 0 for c in coefficients.values())
                    and all(c >= 0 and (c == 0 or solution[k] >= 0) for k, c in coefficients.items())):
                utilization = _finite(100.0 * lhs / rhs)
            rows.append(ConstraintResourceAnalysis(
                name=name, kind=kind, operator=operator, lhs=lhs, rhs=rhs,
                residual=residual, violation=violation, tolerance=tolerance,
                slack=-residual if operator == '<=' else None,
                excess=residual if operator == '>=' else None,
                distance_to_boundary=abs(residual), utilization_percent=utilization,
                is_active=active, is_feasible=violation <= tolerance,
                potential_bottleneck=active and utilization is not None,
            ))

        for constraint in snapshot['constraints']:
            append(constraint['name'], 'constraint', constraint['operator'],
                   constraint['rhs'], constraint['coefficients'])
        for variable in variables:
            name = variable['name']
            lower = variable.get('lower_bound', 0.0)
            upper = variable.get('upper_bound')
            if lower is not None:
                append(name, 'lower_bound', '>=', lower, {name: 1.0})
            if upper is not None:
                append(name, 'upper_bound', '<=', upper, {name: 1.0})
        if not all(row.is_feasible for row in rows):
            for row in rows:
                row.potential_bottleneck = False
        return rows
    except (KeyError, TypeError, AttributeError, OverflowError) as exc:
        raise ValueError('Snapshot ou solução inválidos para análise.') from exc


def analyze_execution(execution):
    if execution.status != 'optimal':
        raise ValueError('A análise requer uma execução ótima.')
    snapshot = execution.analysis_snapshot
    if not isinstance(snapshot, dict) or 'model' not in snapshot or 'values' not in snapshot:
        raise ValueError('Snapshot histórico ausente ou inválido. Execute novamente o modelo.')
    resources = analyze_resources(snapshot['model'], snapshot['values'])
    return ResourceAnalysisResponse(
        execution_id=execution.id, problem_id=execution.problem_id,
        scenario_id=execution.scenario_id, status=execution.status,
        objective_value=execution.objective_value,
        is_feasible=all(row.is_feasible for row in resources), resources=resources,
    )


def analisar_recursos(db, execution_id):
    """Compatibility entry point for callers using a database session."""
    from app.repositories.resource_analysis_repository import get_execution
    execution = get_execution(db, execution_id)
    if execution is None:
        raise LookupError('Execução não encontrada.')
    return analyze_execution(execution)
