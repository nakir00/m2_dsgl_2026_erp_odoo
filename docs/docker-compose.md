# Docker Compose Environment

This repository uses Docker Compose as the default local environment for Odoo 18 and PostgreSQL.

## Structure

```text
.
├── docker-compose.yml
├── .env.example
├── odoo/
│   ├── Dockerfile
│   └── odoo.conf
└── custom_addons/
```

## First Start

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env` if necessary, then start Odoo:

```bash
docker compose up -d --build
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
