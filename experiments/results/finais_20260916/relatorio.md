# Experimentos finais — resultados medidos

Instâncias aprovadas: **152/152**.

## Por classe

| Grupo/classe | Casos | Aprovados |
|---|---:|---:|
| classes/factivel_limitado | 35 | 35 |
| classes/factivel_misto | 35 | 35 |
| classes/inviavel | 15 | 15 |
| classes/ilimitado | 15 | 15 |
| escala/factivel_limitado | 50 | 50 |
| aplicacao/aplicacao | 2 | 2 |

## Comportamento por tamanho

Tempos: mediana entre instâncias das medianas de cada execução. Iterações: medianas entre instâncias.

| Variáveis | Restrições reais | Casos | Próprio (ms) | HiGHS (ms) | Fase I | Fase II | HiGHS nit |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 15 | 10 | 0.5693 | 1.2233 | 3 | 5.5 | 3 |
| 10 | 30 | 10 | 1.6459 | 1.3287 | 4 | 15 | 8.5 |
| 20 | 60 | 10 | 7.34975 | 1.76385 | 2 | 49 | 14 |
| 50 | 150 | 10 | 209.515 | 4.0472 | 0 | 308.5 | 32.5 |
| 100 | 300 | 10 | 4979.33 | 11.6478 | 0 | 1501 | 54 |

Maior erro normalizado: 9.12385200677e-15.
Maior erro relativo convencional (referência não nula): 9.12385200677e-15.

## Metodologia e limites

- Erro relativo = |Z próprio − Z HiGHS| / |Z HiGHS|; nulo se a referência é zero.
- Erro normalizado = |diferença| / max(1, |Z HiGHS|); aprovação exige ≤ 1e-7 e factibilidade dos dois vetores com tolerância absoluta 1e-7.
- Inviáveis e ilimitados não possuem erro de objetivo definido: campos vazios, nunca zero artificial.
- Aprovação exige status esperado pela construção e aprovação em todas as repetições. Exceções são registradas como falhas.
- Um aquecimento por instância/solver; ordem alternada, cinco repetições por padrão; preparação do solver e escrita de arquivos fora do cronômetro.
- Tempos incluem conversão de entradas e adaptadores, mas excluem HTTP, interface, banco e geração. Medem os solvers via suas interfaces Python.
- HiGHS usa scipy.optimize.linprog(method="highs") com presolve e escolhas automáticas padrão. nit não é diretamente equivalente às iterações do Simplex em duas fases.
- Tamanhos reais incluem n limites superiores: 2n linhas aleatórias + n limites, total 3n. Escala cobre apenas a família factível limitada; não generalizar a todas as classes.
- Resultados de tempo são locais, sujeitos a carga do sistema e bibliotecas. Não representam superioridade universal de um algoritmo.
- Feixes: modelo reconstruído com coeficientes inferidos. Mix: caso sintético. Instâncias, sementes, amostras e ambiente acompanham o relatório.

## Falhas

Nenhuma falha nesta execução.
