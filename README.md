# M2 DSGL 2026 ERP Odoo

Repository for the M2 DSGL 2026 ERP Odoo exam project.

Main module:

```text
pharmacie_management
```

## Project workflow

This repository uses a simple GitHub-native workflow:

- GitHub Issues for tickets.
- GitHub Projects for status tracking.
- Pull requests for code review.
- Codex as a development assistant for analysis, implementation, tests, and PR preparation.

Recommended project columns:

```text
Backlog
Todo
In Progress
Review
Done
```

See [docs/github-workflow.md](docs/github-workflow.md) for issue, branch, and pull request conventions.

## Local Odoo Environment

The project uses Docker Compose as the default local environment:

```bash
cp .env.example .env
docker compose up -d --build
```

Then open:

```text
http://localhost:8072
```

See [docs/docker-compose.md](docs/docker-compose.md) for the full local setup.

## VS Code

Recommended VS Code extensions are listed in `.vscode/extensions.json`.

See [docs/vscode.md](docs/vscode.md) for details.
