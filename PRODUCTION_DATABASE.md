# Production Database Setup

## Local development

If `DATABASE_URL` is not configured, the application uses:

`data/security_guard.db`

## Production

Set `DATABASE_URL` to a PostgreSQL connection string through Streamlit Cloud
Secrets (or an environment variable outside Streamlit Cloud).

Example:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
```

Never commit credentials to GitHub.

## Fresh PostgreSQL database

Run:

```text
alembic upgrade head
```

The production migration chain starts at:

```text
64c1dcdf57c3  create production baseline
        |
        v
8b7f1f0c1d4a  align guard employment fields
```

## Existing legacy SQLite database

Do not run `alembic upgrade head` blindly against the existing database because
its old `alembic_version` points to a migration history that has now been
replaced by the production baseline.

For the controlled SQLite -> PostgreSQL migration, first create a backup,
then normalize the legacy schema, and finally copy the data into PostgreSQL.
That migration procedure will be added as the next deployment step.
