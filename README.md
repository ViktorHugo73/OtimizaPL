O README atual descreve apenas o núcleo matemático. Esta versão apresenta a aplicação completa, seu contexto acadêmico e as instruções de uso:

# OtimizaPL

**Sistema de apoio à decisão baseado em Programação Linear e no Método Simplex.**

O OtimizaPL permite cadastrar problemas de otimização, calcular soluções, analisar a utilização de recursos e comparar cenários por meio de uma interface web.

Desenvolvido no contexto de um Trabalho de Conclusão de Curso, o projeto busca facilitar o uso de modelos de otimização por pessoas com pouca familiaridade com a modelagem matemática. Seu caso de aplicação envolve uma oficina de feixes de molas, embora o sistema aceite outros problemas de Programação Linear.

## Funcionalidades

- Cadastro guiado de problemas em cinco etapas.
- Minimização e maximização da função objetivo.
- Definição de variáveis, limites e restrições lineares.
- Resolução pelo Método Simplex de duas fases.
- Apresentação dos valores calculados e interpretação dos resultados.
- Análise de folgas, excessos e utilização dos recursos.
- Identificação de restrições ativas e gargalos potenciais.
- Criação e comparação de cenários.
- Consulta ao histórico de execuções.
- Preservação do modelo executado por meio de snapshots.
- Salvamento manual de rascunhos no navegador.
- Exclusão definitiva mediante confirmação.

## Tecnologias

| Camada | Tecnologias |
|---|---|
| Interface | React, TypeScript e CSS |
| Desenvolvimento do frontend | Vite |
| API | Python e FastAPI |
| Motor matemático | Implementação própria do Simplex de duas fases |
| Persistência | SQLAlchemy e PostgreSQL |
| Migrações | Alembic |
| Validação numérica | SciPy/HiGHS |
| Testes | pytest e testes de interface com Playwright |

O motor Simplex permanece separado da interface e dos serviços de persistência.

## Organização do projeto

```text
app/
├── api/routes/       # Endpoints da API
├── schemas/          # Contratos de entrada e saída
├── services/         # Serviços da aplicação
├── repositories/     # Acesso aos dados
├── db_models/        # Modelos de persistência
└── database/         # Conexão e sessões do banco

frontend/
├── src/pages/        # Páginas da aplicação
├── src/components/   # Componentes reutilizáveis
├── src/api/          # Comunicação com o backend
├── src/types/        # Tipos TypeScript
└── tests/            # Testes do frontend

motor/                # Implementação do Simplex
models/               # Modelos de validação
examples/             # Exemplos de cadastro
validacao/            # Comparação com solver de referência
experiments/          # Experimentos computacionais
tests/                # Testes automatizados do backend
alembic/              # Migrações do banco
```

## Execução local

As instruções abaixo utilizam Windows e PowerShell.

### 1. Obter o projeto

```powershell
git clone https://github.com/ViktorHugo73/OtimizaPl.git
cd OtimizaPl
```

### 2. Preparar o ambiente Python

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar o banco

Disponibilize uma instância PostgreSQL e crie um banco para a aplicação.

Na raiz do projeto, crie um arquivo `.env` com a conexão correspondente:

```dotenv
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@localhost:5432/tcc_otimizador
```

Substitua `USUARIO` e `SENHA` pelas credenciais do seu ambiente. Não publique o arquivo `.env`.

Aplique as migrações:

```powershell
alembic upgrade head
```

### 4. Iniciar a API

Com o ambiente virtual ativado:

```powershell
uvicorn app.main:app --reload
```

Documentação interativa: http://127.0.0.1:8000/docs

### 5. Iniciar o frontend

Em outro terminal, na raiz do projeto:

```powershell
cd frontend
npm install
npm run dev
```

Acesse: http://127.0.0.1:5173

Por padrão, o frontend consulta a API em `http://127.0.0.1:8000/api/v1`. Para outro endereço, configure `VITE_API_URL` no ambiente do frontend.

## Como utilizar

1. Consulte a página **Como usar?**.
2. Acesse **Novo problema**.
3. Informe nome e descrição.
4. Cadastre as decisões que serão calculadas.
5. Defina o objetivo e seus coeficientes.
6. Adicione as restrições e os limites.
7. Revise o modelo e selecione **Salvar e resolver**.
8. Consulte o resultado e a análise de recursos.
9. Crie cenários para comparar alternativas.

## Testes e verificação

Na raiz do projeto, com o ambiente virtual ativado:

```powershell
python -m pytest -q
```

Para verificar TypeScript e gerar o frontend:

```powershell
npm --prefix frontend run build
```

Para executar os testes das regras do formulário, utilizando Node.js 24:

```powershell
node --test frontend/tests/problemForm.test.mjs
```

## Contexto acadêmico

O projeto investiga como uma aplicação computacional pode tornar modelos de otimização mais acessíveis e apoiar a análise de alternativas em pequenas empresas.

A oficina de feixes de molas constitui o contexto de aplicação. Um segundo caso de mix de produção e experimentos com o solver HiGHS complementam a validação do sistema.

O objetivo é apoiar decisões com informações quantitativas, mantendo explícitas as hipóteses e limitações do modelo.
