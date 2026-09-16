"""Command-line interface for VibeSpec."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__
from .bundle import VibeSpecError, generate_bundle, validate_bundle

SAMPLE = """# Application idea

A booking application for independent tutors. Students search by subject, reserve available times, and receive email reminders. Tutors manage availability. Start with one region and no payments.
"""


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="vibespec", description="Generate deterministic project specifications offline.")
    result.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = result.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="write a documented sample idea file")
    init.add_argument("path", nargs="?", type=Path, default=Path("idea.md"))
    init.add_argument("--force", action="store_true", help="replace an existing sample file")

    generate = commands.add_parser("generate", help="generate a specification bundle")
    source = generate.add_mutually_exclusive_group(required=True)
    source.add_argument("--idea", help="rough application idea as command-line text")
    source.add_argument("--input", type=Path, help="UTF-8 Markdown or text idea file")
    generate.add_argument("--name", required=True, help="safe project name")
    generate.add_argument("-o", "--output", type=Path, help="output directory (default: ./NAME)")
    generate.add_argument("--force", action="store_true", help="replace existing generated files")

    validate = commands.add_parser("validate", help="verify completeness and checksums")
    validate.add_argument("bundle", type=Path)

    export = commands.add_parser("export-agents", help="export portable coding-agent instructions")
    export.add_argument("bundle", type=Path)
    export.add_argument("-o", "--output", type=Path, help="destination file (default: stdout)")
    export.add_argument("--force", action="store_true", help="replace an existing output file")
    return result


def _write_sample(path: Path, force: bool) -> None:
    target = path.expanduser().resolve()
    if target.exists() and not force:
        raise VibeSpecError(f"refusing to overwrite {target}; pass --force")
    if target.exists() and target.is_dir():
        raise VibeSpecError(f"sample path is a directory: {target}")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(SAMPLE, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise VibeSpecError(f"cannot write sample {target}: {exc}") from exc
    print(f"Initialized sample idea: {target}")


def _read_input(path: Path) -> str:
    try:
        if not path.is_file():
            raise VibeSpecError(f"input file does not exist or is not a file: {path}")
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise VibeSpecError(f"cannot read UTF-8 input {path}: {exc}") from exc


def _export(bundle: Path, output: Path | None, force: bool) -> None:
    validate_bundle(bundle)
    source = bundle.expanduser().resolve() / "AGENTS.md"
    if output is None:
        sys.stdout.write(source.read_text(encoding="utf-8"))
        return
    target = output.expanduser().resolve()
    if target.exists() and not force:
        raise VibeSpecError(f"refusing to overwrite {target}; pass --force")
    if target.exists() and target.is_dir():
        raise VibeSpecError(f"export path is a directory: {target}")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    except OSError as exc:
        raise VibeSpecError(f"cannot export agent instructions: {exc}") from exc
    print(f"Exported agent instructions: {target}")


def run(args: argparse.Namespace) -> None:
    if args.command == "init":
        _write_sample(args.path, args.force)
    elif args.command == "generate":
        idea = args.idea if args.idea is not None else _read_input(args.input)
        destination = args.output if args.output is not None else Path(args.name)
        output = generate_bundle(args.name, idea, destination, force=args.force)
        print(f"Generated VibeSpec bundle: {output}")
    elif args.command == "validate":
        validate_bundle(args.bundle)
        print(f"Valid VibeSpec bundle: {args.bundle.expanduser().resolve()}")
    elif args.command == "export-agents":
        _export(args.bundle, args.output, args.force)


def main(argv: list[str] | None = None) -> int:
    try:
        run(parser().parse_args(argv))
        return 0
    except VibeSpecError as exc:
        print(f"vibespec: error: {exc}", file=sys.stderr)
        return 2

