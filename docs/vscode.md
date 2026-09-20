# VS Code Recommendations

This repository includes VS Code workspace recommendations in `.vscode/extensions.json`.

## Recommended Extensions

| Extension | Purpose |
| --- | --- |
| Python | Python support for Odoo module code. |
| Pylance | Better Python analysis and navigation. |
| Odoo | Odoo-specific helpers and snippets. |
| XML | XML validation and editing for Odoo views, security, data, and QWeb reports. |
| YAML | YAML support for Docker Compose. |
| Docker | Dockerfile and Docker Compose support. |
| GitHub Pull Requests | Work with GitHub issues and pull requests from VS Code. |
| Markdownlint | Keep README and documentation files clean. |

## Notes

The project runs through Docker Compose, so no local Python virtual environment is required to start Odoo.

Custom Odoo modules should be created under:

```text
custom_addons/
```
