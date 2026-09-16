# Security Policy

## Supported versions

Security fixes are provided for the latest released minor version.

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |
| Earlier | No |

## Reporting a vulnerability

Do not open a public issue. Use GitHub's **Security → Report a vulnerability** workflow for this repository to send a private report to the maintainers. Include the affected version, operating system, reproduction steps, impact, and any suggested mitigation. Remove secrets and private project ideas from logs or sample files before attaching them.

Maintainers aim to acknowledge a report within five business days, provide an initial assessment within ten business days, and coordinate a fix and disclosure timeline with the reporter. These targets are best-effort for a volunteer project.

## Security model

VibeSpec is an offline document generator. It does not need network access, API keys, a database, or telemetry. It treats idea files and bundles as untrusted local input: paths and project names are validated, existing output is protected by default, and manifests detect changed or missing generated documents.

VibeSpec does not sandbox the directory in which it runs and does not authenticate manifest contents. Run it with ordinary user privileges, inspect source ideas before sharing them, and obtain releases from a trusted source. Never store credentials in an idea file; generated specifications may repeat input text.
