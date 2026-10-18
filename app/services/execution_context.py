"""Read immutable execution context; never rebuild from current problem parameters."""
from copy import deepcopy
from math import isfinite
from app.services.resource_analysis_service import analyze_resources


def stored_model(execution):
    try:
        model = execution.analysis_snapshot['model']
        if model['objective_type'] not in ('min', 'max'):
            raise ValueError()
        names = [v['name'] for v in model['variables']]
        if any(not isinstance(n, str) or not n.strip() for n in names):
            raise ValueError()
        for v in model['variables']:
            if not isfinite(float(v['objective_coefficient'])):
                raise ValueError()
        analyze_resources(model, dict.fromkeys(names, 0.0))
        return deepcopy(model)
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        raise ValueError('Snapshot histórico ausente ou inválido; não é possível copiar o modelo desta execução.') from None


def execution_context(execution):
    context = dict(problem_name=execution.problem.name, objective_type=None,
                   snapshot_available=False, recorded_variables=None)
    try:
        model = stored_model(execution)
    except ValueError:
        return context
    context.update(objective_type=model['objective_type'], snapshot_available=True)
    if execution.status == 'optimal':
        try:
            values = execution.analysis_snapshot['values']
            analyze_resources(model, values)
            context['recorded_variables'] = [dict(name=v['name'], value=float(values[v['name']])) for v in model['variables']]
        except (KeyError, TypeError, ValueError, OverflowError):
            pass
    return context
