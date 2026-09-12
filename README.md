# TCC Otimizador — Núcleo Matemático

Estado atual: motor Simplex isolado + validação com SciPy/HiGHS + testes + benchmark.

## Instalação (Windows / PowerShell)

```powershell
cd caminho\para\tcc_otimizador
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Testes

```powershell
pytest -v
```

O teste `test_artigo_v1_0_definitivo` ficará `SKIPPED` enquanto
`models/artigo_v1_0.py` estiver com `MODELO_FECHADO = False`. Isso é intencional.

## Benchmark inicial

```powershell
python experiments\executar_benchmark.py
```

Saídas:

- `experiments/results/resultados.csv`
- `experiments/results/ambiente.json`
- `experiments/instances/P001.json` etc.

## Regra metodológica

Não preencha `TR`, `TS`, `H`, `MR`, `MS` ou `L` por inferência. Eles devem ser
confirmados na planilha/dados-fonte usados no artigo. Só então o modelo oficial
`artigo_v1_0` deve ser desbloqueado.
