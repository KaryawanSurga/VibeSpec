# Developer tool example

This idea exercises command-line, local-file, structured-output, security-boundary, error-status, and cross-platform rules. Its explicit constraints should appear in security and out-of-scope sections rather than being weakened by defaults.

From the repository root after installing VibeSpec:

```bash
vibespec generate --input examples/developer-tool/idea.md \
  --name dependency-report -o generated/dependency-report
vibespec validate generated/dependency-report
vibespec export-agents generated/dependency-report
```

The final command prints the agent instructions to standard output. Generated artifacts are local build products and are intentionally not committed.
