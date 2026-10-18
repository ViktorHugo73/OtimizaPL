# Experimentos finais de validação

O executor `experiments/experimentos_finais.py` compara o Simplex próprio v1.0 com o HiGHS via SciPy, sem alterar o motor ou o banco da aplicação.

## Reproduzir

Na raiz do projeto, com as dependências instaladas no ambiente virtual, execute no PowerShell:

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
.\.venv\Scripts\python.exe -m experiments.experimentos_finais --output experiments/results/nova_execucao --repetitions 5 --scale-instances 10
```

Use uma pasta de saída nova a cada execução. O programa recusa sobrescrever resultados anteriores e retorna código 1 se qualquer instância falhar. Evite outras tarefas pesadas durante a medição. As variáveis de ambiente solicitam um limite de threads às bibliotecas correspondentes; não substituem uma auditoria do paralelismo interno de cada biblioteca.

## Desenho experimental

- 35 problemas factíveis limitados e 35 factíveis com restrições mistas.
- 15 inviáveis e 15 ilimitados, com classificação esperada pela construção.
- 50 problemas de escala: dez por tamanho, com 5, 10, 20, 50 e 100 variáveis; respectivamente 15, 30, 60, 150 e 300 restrições reais.
- Dois casos de aplicação: feixes de mola reconstruído e mix de produção sintético.
- Um aquecimento por solver e instância, seguido de cinco repetições medidas, alternando a ordem dos solvers. Total: 152 instâncias e 760 pares de amostras medidas.

Para soluções ótimas, a aprovação exige erro normalizado no objetivo de até 1e-7 e factibilidade de ambos os vetores com tolerância absoluta de 1e-7. Também são registrados erro absoluto e erro relativo convencional. Quando o objetivo de referência é zero, o erro relativo convencional fica sem valor; o erro normalizado continua definido. Casos inviáveis ou ilimitados não recebem erro de objetivo artificialmente igual a zero.

São preservados os tempos e as iterações de cada repetição. O resumo utiliza medianas de tempo e iterações, e máximos dos erros e violações. Todas as repetições precisam passar. O relatório por tamanho apresenta a mediana entre as medianas das instâncias.

## Evidências

A execução de 16/09/2026 está em `experiments/results/finais_20260916/`:

- `relatorio.md`: resultados por classe e tamanho, critérios e limitações.
- `resultados.csv`: uma linha por instância.
- `amostras.csv`: uma linha por repetição, com tempos, erros, status e iterações dos dois solvers.
- `instances/`: entradas matemáticas completas e sementes.
- `ambiente.json`: versões, ambiente, parâmetros, horários e hashes dos arquivos usados.

## Interpretação no TCC

A concordância com o HiGHS e a verificação independente da factibilidade fornecem evidência de correção nos casos testados; não constituem prova de correção para toda programação linear. Não se exige igualdade dos vetores ótimos, pois podem existir ótimos alternativos.

O HiGHS é chamado com `method="highs"` e configurações automáticas padrão, incluindo presolve. Seu campo `nit` não equivale diretamente à soma das iterações das fases I e II do motor próprio. Compare tempos das interfaces Python e qualidade das respostas; trate contagens de iterações como descrição dos respectivos procedimentos.

Os tempos excluem API, persistência, interface e geração das instâncias. A análise de escala cobre a família factível limitada e a faixa de tamanhos medida. Não permite inferir uma lei geral de complexidade, nem desempenho para matrizes industriais esparsas. Os dois casos de aplicação também têm limites: os feixes usam coeficientes reconstruídos e o mix é sintético.

## Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Os testes adicionais verificam o desenho experimental, a contagem real de restrições, o tratamento do objetivo zero, as classificações inviável/ilimitado e a rejeição de erros coincidentes nos dois solvers.
