# Cadastro de problemas em cinco etapas

Implementação de 13/10/2026 na aplicação existente, em `/problems/new`.

## Backup anterior à implementação

`backup-cadastro-etapas-20261013-002316/` contém 411 arquivos de código, configurações e evidências, com `backup-manifest.json` (SHA-256). Foram excluídos Git, dependências, caches, dist e backups anteriores. Esse é um backup dos arquivos do projeto, não uma exportação do PostgreSQL. Não houve alteração de dados de produção nem migração do banco.

## Funcionalidades

1. Identificação: nome, descrição e segmento opcional.
2. Decisões: identificador, descrição amigável, limites, adição e exclusão confirmada.
3. Objetivo: minimizar/maximizar, contribuição por unidade e prévia automática.
4. Condições: coeficientes de todas as decisões em matriz com rolagem horizontal, operador e limite.
5. Revisão: resumo completo e visualização matemática complementar, Voltar, Salvar e Salvar e resolver.

Os dados permanecem em memória ao navegar entre as etapas. Identificadores internos estáveis vinculam variáveis a coeficientes; renomear preserva esses vínculos e excluir remove as contribuições associadas. O formulário não impõe um máximo de duas variáveis. A validação aceita valores negativos nos coeficientes e no RHS, mantém a não negatividade das variáveis e não rejeita por conta própria modelos inviáveis ou ilimitados.

Salvar reutiliza `POST /api/v1/problems`. Salvar e resolver também usa `POST /api/v1/problems/{id}/solve`, abrindo `/problems/{id}/executions?execution={execution_id}`. O resultado vem da API e do motor existentes. Se a resolução falhar após o salvamento, o ID criado é preservado, a edição fica bloqueada e a resolução pode ser repetida sem duplicar o cadastro; links permitem conferir problema e histórico. Em caso de perda de resposta de rede, o usuário é orientado a consultar os registros antes de repetir a operação, pois os endpoints atuais não possuem chave de idempotência.

## Decisões de escopo

- O segmento é incluído como `Segmento: ...` na descrição persistida; não é uma coluna nem um filtro estruturado. A interface informa esse comportamento. Assim, classificação básica permanece consultável sem alteração de schema, migração ou contrato.
- Não foi implementado rascunho persistente. Recarregar a página ou sair dela descarta dados ainda não salvos. Rascunhos com recuperação e versionamento ficam para evolução posterior.
- O protótipo de outra conversa não acompanhou as instruções; a implementação segue os requisitos escritos e os estilos existentes.
- O motor, o backend, as tabelas e os snapshots existentes não foram alterados.

## Arquivos

Alterados:
- `frontend/src/pages/CreateProblemPage.tsx`: fluxo integrado.
- `frontend/src/pages/createProblem.css`: apresentação responsiva e estados.
- `frontend/src/api/client.ts`: mensagens legíveis para erros estruturados da API.

Criados:
- `frontend/src/components/ProblemField.tsx`: campo reutilizável com rótulo, ajuda, erro e atributos de acessibilidade.
- `frontend/src/components/problemForm.ts`: estado, validação, sincronização da matriz e conversão para o contrato atual.
- `frontend/src/api/apiError.ts`: normalização de erros Pydantic.
- `frontend/tests/problemForm.test.mjs`: oito testes de regras e serialização.
- `frontend/tests/wizard.e2e.cjs`: teste de navegador com a API real isolada.
- `frontend/tests/wizard_api.py`: servidor de teste com SQLite definido explicitamente por variável de ambiente.

Reutilizados: `createProblem`, `solveProblem`, tipos `ProblemCreate`, exemplo de mix, navegação React Router e tela existente de histórico/recursos. Não houve criação de uma aplicação independente.

## Validação realizada

- TypeScript e build Vite: aprovados.
- ESLint dos arquivos TypeScript alterados/criados: aprovado.
- Testes das regras do formulário: 8 aprovados, com Node 24.
- Suíte completa do backend: 113 aprovados, com dois avisos de depreciação de dependências.
- Navegador, API FastAPI real, motor próprio e SQLite isolado: navegação nas cinco etapas; validações; preservação dos campos ao voltar; duas e três variáveis; renomear/adicionar/excluir e sincronizar matriz; leitura após recarregar; salvar sem execução; salvar e resolver; resultado ótimo; status inviável e ilimitado; histórico e cenário; erros 422 legíveis; recuperação de falha após salvar sem duplicar o problema.
- Conferência em 1280 px e 390 px; rolagem horizontal limitada à matriz, sem ultrapassar a largura do formulário. Sem erros JavaScript nos fluxos exercitados.

Os testes de navegação utilizaram uma base exclusiva em `tmp/wizard/ui-validation.sqlite`, fora do banco configurado da oficina. Os problemas de teste não foram cadastrados em produção. A verificação global anterior do ESLint já apresentava problemas em ComparisonPage, ProblemPage e ScenariosPage, fora deste escopo; não se declara o lint global aprovado.

## Reproduzir os testes

Na raiz do projeto:

```powershell
npm.cmd --prefix frontend run build
node --test frontend/tests/problemForm.test.mjs
.\.venv\Scripts\python.exe -m pytest -q
```

Para a conferência completa no navegador, iniciar Vite na porta 5173. Em outro terminal, definir `WIZARD_TEST_DB` com um caminho absoluto novo para um arquivo SQLite de teste e executar `python frontend/tests/wizard_api.py` com o ambiente virtual do projeto. O runner exige essa variável e usa a porta 8011. Não informar um banco de uso real.

Com Playwright e Edge disponíveis, executar `node frontend/tests/wizard.e2e.cjs`. A variável opcional `PLAYWRIGHT_MODULE` pode indicar o caminho de uma instalação de Playwright já disponível; `WIZARD_TEST_OUTPUT` escolhe a pasta dos registros e capturas. O script redireciona as chamadas da interface para a porta 8011. Não iniciar o teste se essa porta estiver sendo usada por outro serviço.

## Recuperar a interface anterior

Parar a interface, restaurar do backup os três arquivos listados como alterados e reconstruir o frontend. Os módulos novos ficam sem uso após a restauração e podem ser preservados para comparação. A recuperação não requer alteração do banco. Conferir o manifesto antes de restaurar; evitar copiar o backup inteiro sobre trabalhos posteriores.

## Atualização conforme referências visuais
Etapas: Identificação, Decisões, Objetivo, Restrições e Revisão. Campos organizados conforme as imagens, com cores adaptadas ao tema da aplicação. Limites opcionais em seção expansível. Rascunho parcial ou completo pode ser salvo manualmente neste navegador e recuperado na primeira etapa; não é sincronizado com o servidor. Esta funcionalidade substitui a limitação anterior de ausência de rascunho persistente. Testes de integração atualizados para os novos controles.
