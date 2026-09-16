# Local Dependency Report CLI

Create a cross-platform command-line developer tool that scans a local project manifest and produces a Markdown or JSON report of direct dependencies, declared versions, and duplicate constraints. It should support an explicit input path, write to standard output by default, optionally write a file, and use meaningful exit codes for malformed manifests or filesystem errors.

The first release must run entirely offline on Windows, macOS, and Linux. It must never execute project code, install packages, contact registries, collect telemetry, or modify the scanned repository.
