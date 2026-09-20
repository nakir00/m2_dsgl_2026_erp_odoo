# Docker Compose Environment

This repository uses Docker Compose as the default local environment for Odoo 18 and PostgreSQL.

## Structure

```text
.
├── docker-compose.yml
├── odoo/
│   └── odoo.conf
└── custom_addons/
```

## First Start

Start Odoo and PostgreSQL:

```bash
docker compose up -d
```

Open Odoo:

```text
http://localhost:8072
```

## Useful Commands

Show running services:

```bash
docker compose ps
```

Follow logs:

```bash
docker compose logs -f odoo
```

Stop services:

```bash
docker compose down
```

Stop services and remove persistent volumes:

```bash
docker compose down -v
```

## Database Access and Backup

PostgreSQL is intentionally available only to the Odoo container. Use Compose to
run administration commands instead of publishing port `5432` on the host.

Create a plain SQL backup of an Odoo database:

```bash
docker compose exec -T db pg_dump -U odoo pharmacie > sauvegarde-pharmacie.sql
```

Restore it into an existing empty database with the same name:

```bash
docker compose exec -T db psql -U odoo pharmacie < sauvegarde-pharmacie.sql
```

Replace `pharmacie` with the database name created from the Odoo database manager.

## Demonstration Scope

The bundled credentials are for local coursework only. Before any public deployment,
use dedicated secrets, disable database listing, restrict network access, add HTTPS,
and define a tested backup and restoration procedure.

## Addons

Custom modules must be placed in:

```text
custom_addons/
```

The exam module will be:

```text
custom_addons/pharmacie_management/
```

After adding or updating a module, restart or update it from Odoo Apps.
