# VS Code Recommendations

This repository includes VS Code workspace recommendations in `.vscode/extensions.json`.

## Recommended Extensions

| Extension | Purpose |
| --- | --- |
| Python | Python support for Odoo module code. |
| Pylance | Better Python analysis and navigation. |
| Odoo | Odoo-specific helpers and snippets. |
| XML | XML validation and editing for Odoo views, security, data, and QWeb reports. |
| YAML | YAML support for Docker Compose and future Kubernetes manifests. |
| Docker | Dockerfile and Docker Compose support. |
| Kubernetes | Useful later if the project simulates deployment with k3d/K3s. |
| GitHub Pull Requests | Work with GitHub issues and pull requests from VS Code. |
| Markdownlint | Keep README and documentation files clean. |
| EditorConfig | Consistent editor behavior across contributors. |

## Notes

The project runs through Docker Compose, so no local Python virtual environment is required to start Odoo.

Custom Odoo modules should be created under:

```text
custom_addons/
```
