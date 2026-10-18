"""Caso sintético, contínuo, independente do estudo de feixes de mola."""
import json
from pathlib import Path

PAYLOAD_PATH = Path(__file__).resolve().parents[1] / 'examples' / 'mix_producao.json'
SOLUCAO_ESPERADA = {'x': [2.0, 6.0, 0.0], 'z': 36.0}


def carregar_payload_mix():
    return json.loads(PAYLOAD_PATH.read_text(encoding='utf-8'))


def carregar_modelo_mix():
    payload = carregar_payload_mix()
    names = [v['name'] for v in payload['variables']]
    coefficients = [{t['variable_name']: t['coefficient'] for t in c['terms']}
                    for c in payload['constraints']]
    return dict(nome=payload['name'], objetivo=payload['objective_type'], variaveis=names,
                c=[v['objective_coefficient'] for v in payload['variables']],
                A=[[row.get(name, 0) for name in names] for row in coefficients],
                b=[c['rhs'] for c in payload['constraints']],
                operadores=[c['operator'] for c in payload['constraints']])
