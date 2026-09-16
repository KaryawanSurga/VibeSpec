# Booking application example

This idea exercises browser application, scheduling, role, notification, privacy, and conflict-handling rules. It also names exclusions that should remain explicit in the generated product specification.

From the repository root after installing VibeSpec:

```bash
vibespec generate --input examples/booking-app/idea.md \
  --name workshop-booking -o generated/workshop-booking
vibespec validate generated/workshop-booking
vibespec export-agents generated/workshop-booking -o generated/workshop-agents.md
```

Re-running generation without `--force` must fail because the bundle exists. Add `--force` only when deliberately replacing it. The `generated/` directory is ignored by Git.
