# Fly.io

Deploy from a clean checkout using the root Dockerfile:

```bash
flyctl auth login
flyctl launch --copy-config --config deploy/fly/fly.toml --no-deploy
flyctl secrets set FALKORDB_HOST=localhost FALKORDB_PORT=6379
flyctl deploy --config deploy/fly/fly.toml
```

Change `app` in `fly.toml` before launch if the default app name is already taken.
