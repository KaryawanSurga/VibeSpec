# Contributing to VibeSpec

Thank you for helping make deterministic project planning more useful. Contributions should preserve VibeSpec's offline, explainable, reproducible behavior.

## Before opening a change

Search existing issues, then open a feature request for changes to bundle structure, public commands, or rule behavior. Bug fixes and documentation improvements may go directly to a pull request when their scope is clear. Never include real credentials, private ideas, or generated bundles containing sensitive product information.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security vulnerabilities belong in the private process described in [SECURITY.md](SECURITY.md), not a public issue.

## Development setup

VibeSpec supports Python 3.11 through 3.13.

```bash
git clone https://github.com/KaryawanSurga/VibeSpec.git
cd vibespec
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
```

On PowerShell, activate with `.\.venv\Scripts\Activate.ps1`.

## Engineering expectations

- Keep runtime dependencies minimal and justify additions in the pull request.
- Preserve offline execution: no network requests, telemetry, or credential discovery.
- Keep generated content deterministic across operating systems. Sort unordered data, emit UTF-8 with normalized newlines, and avoid clocks, random values, absolute paths, or platform-specific separators in output.
- Validate at boundaries and produce actionable, non-sensitive errors.
- Protect user files by default; destructive behavior requires an explicit option.
- Update documentation and the changelog when behavior visible to users changes.
- Add tests for success, errors, empty input, overwrite protection, and tamper detection as relevant.

## Testing changes

Run the full suite before submitting:

```bash
pytest
```

For generator changes, generate the same example twice in separate temporary directories and compare all bytes. Validate both example bundles. Do not commit caches, virtual environments, distributions, or ad hoc generated output.

## Pull requests

Keep commits focused and explain the user impact and trade-offs. Complete the pull request checklist, link the relevant issue, and include exact test commands and results. Maintainers may request changes when a contribution makes rules opaque, weakens overwrite safety, or adds online behavior to the default path.

## Releases

Maintainers update the version and changelog, run the full matrix, verify the installed console entry point from a clean environment, and manually exercise both examples. Tags and releases are created only after approval and merge.
