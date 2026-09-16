# VibeSpec

VibeSpec turns a rough application idea into a consistent, implementation-ready specification bundle. It is a deterministic, offline CLI for developers who want the speed of “vibe coding” without silently invented requirements, cloud services, telemetry, or a paid AI provider.

Given the same idea, project name, and options, VibeSpec writes byte-for-byte identical output. Its generated documents make defaults and assumptions explicit so a human can review them before handing the work to a coding agent.

## What it generates

Every bundle is a self-contained project directory:

```text
my-booking-app/
├── PRODUCT_SPEC.md
├── ARCHITECTURE.md
├── TASKS.md
├── ACCEPTANCE_CRITERIA.md
├── AGENTS.md
└── vibespec.json
```

The bundle covers target users, goals, assumptions, functional and non-functional requirements, edge and error states, security, explicit exclusions, technology recommendations with rationale, architecture, risks, dependency-ordered tasks, role ownership, testable acceptance criteria, and prompts for common coding-agent roles. The manifest records format metadata and content hashes used by validation.

## Requirements

- Python 3.11, 3.12, or 3.13
- No network access or API key

## Installation

From a clean checkout, create an isolated environment and install the package:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Or on PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install VibeSpec:

```bash
python -m pip install .
vibespec --version
```

For development, use `python -m pip install -e ".[dev]"`.

## Quick start

Create an editable sample idea, generate a bundle, and verify it:

```console
$ vibespec init idea.md
Initialized sample idea: /work/vibespec/idea.md
$ vibespec generate --input idea.md --name neighborhood-booking -o ./specs/neighborhood-booking
Generated VibeSpec bundle: /work/vibespec/specs/neighborhood-booking
$ vibespec validate ./specs/neighborhood-booking
Valid VibeSpec bundle: /work/vibespec/specs/neighborhood-booking
```

Paths are resolved to absolute paths in command output; `/work/vibespec` above represents the checkout directory.

You can also supply a short idea directly:

```bash
vibespec generate --idea "A private booking tool for a neighborhood workshop" \
  --name neighborhood-booking -o ./specs/neighborhood-booking
```

VibeSpec never replaces generated files unless `--force` is explicitly supplied:

```bash
vibespec generate --input idea.md --name neighborhood-booking -o ./specs/neighborhood-booking --force
```

Review the generated assumptions and exclusions before implementation. Rule-based generation is deliberately transparent; it does not claim to understand every nuance of free-form intent.

## Command reference

Run `vibespec COMMAND --help` for the authoritative option list.

### `vibespec init [PATH]`

Writes a sample idea file that demonstrates useful input structure. The default path is `idea.md`. Existing files are protected unless `--force` is provided.

### `vibespec generate`

Generates a complete bundle. Supply exactly one input source: `--idea TEXT` or `--input PATH`. `--name NAME` sets the safe directory/project identifier. Without `-o`, the bundle is written to `./NAME`; `-o DIR` selects a different target directory. Use `--force` only when replacing an existing bundle intentionally.

```bash
vibespec generate --input examples/booking-app/idea.md \
  --name workshop-booking -o ./generated/workshop-booking
```

### `vibespec validate BUNDLE`

Checks the manifest schema, required files, recorded hashes, and document completeness. A missing or modified generated file fails with a useful message and a non-zero exit status.

### `vibespec export-agents BUNDLE`

Exports the generated agent instructions to standard output, or to a file with `-o PATH`. This is convenient when a coding-agent tool expects a dedicated instruction file. Existing destination files remain protected unless `--force` is supplied.

```bash
vibespec export-agents ./generated/workshop-booking -o ./AGENTS.md
```

## Exit status

`0` means success. Invalid arguments or malformed ideas, unsafe names, path conflicts, I/O failures, and invalid bundles return non-zero status. Diagnostics are written to standard error. Generation stages content before replacing a target, so a failed command does not leave a half-written bundle.

## Examples

- [`examples/booking-app`](examples/booking-app) describes a community workshop booking product.
- [`examples/developer-tool`](examples/developer-tool) describes a local command-line dependency report.

Generate and validate either example with the commands in its README. Generated bundles are intentionally not committed: reproducibility is exercised by the test suite, while keeping examples easy to inspect.

## Determinism and privacy

Generation is a pure, local transformation of UTF-8 input and explicit options. Stable ordering, normalized newlines, fixed templates, and canonical JSON keep results reproducible across supported platforms. VibeSpec does not use the network, collect telemetry, inspect unrelated files, or read environment credentials. See [Rule engine](docs/rule-engine.md) for the exact inference boundaries.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

The CI matrix runs the suite on Python 3.11, 3.12, and 3.13. Architecture and extension seams are documented in [Architecture](docs/architecture.md). Contribution and disclosure guidance is in [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## Limitations

- VibeSpec applies explainable heuristics; it does not discover unstated product intent.
- Recommendations are deliberately conservative and generic, not a substitute for architecture review.
- It does not call LLMs, install dependencies, generate application source code, or execute generated tasks.
- English prose is the only supported output language in v0.1.0.
- The manifest detects accidental or intentional edits but is not a cryptographic signature or trust system.

Future provider integrations can be built behind the documented rule-engine boundary, but the default offline engine will remain usable and deterministic.

## License

VibeSpec is available under the [MIT License](LICENSE).
