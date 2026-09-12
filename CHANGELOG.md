# Changelog

## 1.0.0

### Implementado

- Simplex de Duas Fases.
- Minimização e maximização.
- Restrições <=, >= e =.
- Variáveis de folga.
- Variáveis de excesso.
- Variáveis artificiais.
- Detecção de inviabilidade.
- Detecção de problema ilimitado.
- Regra de Bland.
- Registro de iterações.
- Verificação independente de factibilidade.
- Comparação automática com SciPy/HiGHS.
- Testes de múltiplos ótimos.
- Testes de degenerescência.
- Testes com RHS negativo.
- Benchmark automatizado.
- Teste de escala.

### Correções

- Correção da remoção de variáveis artificiais após a Fase I.
- Correção da base singular identificada pela instância P045.

### Validação

- Modelo auditado do artigo.
- Comparação com SciPy/HiGHS.
- Bateria automatizada de problemas de Programação Linear.
- Testes de regressão.