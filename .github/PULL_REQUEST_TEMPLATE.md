## Summary

Describe the user-visible outcome and why the change is needed.

## Decisions and trade-offs

Explain changes to public commands, manifest semantics, generation rules, dependencies, or architecture. State alternatives considered when relevant.

## Verification

List exact commands and results, including supported Python versions exercised.

## Checklist

- [ ] Tests cover success and relevant failure/edge cases.
- [ ] Repeated generation remains byte-for-byte deterministic.
- [ ] Existing files remain protected unless force is explicit.
- [ ] The default workflow remains offline and telemetry-free.
- [ ] No credentials, caches, virtual environments, builds, or private idea data are included.
- [ ] User-facing behavior is documented and the changelog is updated when appropriate.
- [ ] Both examples still generate and validate when generator behavior changes.
