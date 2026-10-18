# Vercel services — pending routing confirmation

Project root: repository root, not frontend/. app uses app.main:app; frontend uses Vite.
Public /api/:path* routes to app, preserving /api/v1. All other paths route to frontend; its SPA rewrite supports reloads of /problems and historical routes.
FastAPI /docs, /redoc and /openapi.json are not exposed by this proposal; they remain available when running FastAPI directly locally.

No bindings are declared: React makes requests in the visitor's browser, not in a Vercel function. Bindings cannot be read at build time or embedded in VITE_* variables. To keep app internal, add a separate server-side proxy with a binding; that would be an architecture change requiring confirmation.

## Environment and data
- Configure DATABASE_URL in Vercel using an externally hosted PostgreSQL connection compatible with SQLAlchemy psycopg (postgresql+psycopg://...). Use the provider's TLS settings. Do not use the localhost development database.
- Keep API_PREFIX=/api/v1. Leave VITE_API_URL unset (defaults to /api/v1) or set it to /api/v1; remove old localhost overrides from Vercel settings.
- Apply `alembic upgrade head` against the selected database before first use. Run migrations once in a controlled release step, not on every function invocation or preview build.
- Use separate preview and production databases. Existing local records are not migrated by deploying code.
- Preserve the repository-level examples/ directory in the build context: the frontend imports its JSON files.
- The current API has no user authorization, including permanent deletion. Use a protected demonstration deployment until access controls are implemented.

## Verification
Run from repository root with a current Vercel CLI supporting services:
```powershell
vercel dev -L
```
Or `vercel dev` with a linked Vercel project. Verify /, /problems/new, a direct historical route reload, /api/v1/health and CRUD on a test database. Check that browser API requests use the same origin and API 404s do not return index.html.

Standalone development still works: run uvicorn app.main:app --reload and npm --prefix frontend run dev. The Vite development proxy forwards /api to localhost:8000 (optional LOCAL_API_URL override, server-side only). It is not a Vercel service binding.

Deployment and vercel dev integration must be validated with the Vercel CLI and actual hosted database; a local frontend build does not confirm deployment success.
