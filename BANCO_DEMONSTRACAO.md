# PostgreSQL de demonstração — OtimizaPL

Preparação local concluída; o recurso hospedado ainda precisa ser criado na conta do usuário.

## Criar no Neon

1. Acesse https://console.neon.tech e entre na sua conta.
2. Crie o projeto `otimizapl-demo`, utilizando uma região próxima da região da API na Vercel. Confira o plano e seus limites antes de confirmar; esta preparação não contrata um plano pago.
3. Crie um banco chamado exatamente `otimizapl_demo` dentro desse projeto. Use dados fictícios. Não importe o banco local da oficina.
4. Em Connect, selecione esse banco e copie a conexão direta (pooling desativado), com SSL.

## Criar as tabelas

Na raiz do repositório:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_demo_database.py
```

Cole a conexão quando o terminal solicitar. A entrada fica oculta. O script não salva a senha, não lê o .env como destino e exige um banco Neon vazio chamado otimizapl_demo. Ele aplica as migrações Alembic e verifica as tabelas. Não imprime a URL nem copia dados reais.

Se o banco já possuir tabelas, o script para. Não apague tabelas para contornar essa proteção; consulte o estado da migração primeiro.

## Conectar à Vercel

No Neon, copie agora a conexão com pooling ativado. Em Vercel → projeto → variáveis de ambiente, configure:

- `DATABASE_URL`: conexão com pooling. Troque somente o prefixo `postgresql://` por `postgresql+psycopg://`, preservando usuário, senha codificada, host, nome do banco e parâmetros de SSL.
- `API_PREFIX`: `/api/v1`.
- `VITE_API_URL`: `/api/v1`, ou deixe ausente.

Nunca coloque a conexão do banco em uma variável VITE_*. Ela deve permanecer no backend. Não use a mesma base para previews de código não confiável. Refaça o deploy após configurar as variáveis.

## Dados de exemplo

Depois que o site estiver funcionando, abra Novo problema → Recuperar rascunho ou carregar exemplo. Carregue o caso de feixes de molas e salve/resolva. O resultado esperado é XR=8, XS=12 e objetivo mínimo 13.200. O mix de produção também está disponível.

O endpoint /api/v1/health verifica a API, mas não confirma acesso ao banco. Confira também a listagem, o cadastro e a resolução de um exemplo.

A aplicação ainda não tem autorização por usuário e permite exclusões definitivas. Proteja o acesso à demonstração; não armazene dados reais neste banco.
