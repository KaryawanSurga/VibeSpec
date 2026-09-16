# Rule engine

VibeSpec's rule engine turns a short idea into a useful starting specification without implying that it understands unstated intent. This document defines where inference stops and defaults begin.

## Processing sequence

1. Decode file input as UTF-8 and normalize whitespace and newlines.
2. Reject an empty idea and validate the explicitly supplied project name.
3. Tokenize case-insensitively for known capability signals. Original input remains available for quoted context.
4. Apply classification rules in a fixed priority order.
5. Add conservative defaults and list them under **Assumptions**.
6. Match explicit negative constraints using a small ordered phrase table and preserve them verbatim as normalized controls.
7. Build one shared specification model.
8. Render every document from that model in fixed order.

Rules are additive where possible. When recommendations conflict, the documented priority order decides the result; filesystem or iteration order never does.

## Signals and profiles

Signals are plain words or phrases associated with broad product capabilities, such as authentication, booking/scheduling, payments, notifications, command-line usage, local files, collaboration, or public APIs. A match adds the corresponding requirements, edge cases, security controls, and tasks.

Negative signals are intentionally narrower than capability signals. Phrases such as offline/no network, no APIs, no telemetry, never execute, never install, and never modify produce explicit project constraints. Those controls appear in product scope, architecture security guidance, and agent instructions, where they override generic role guidance. Unrecognized prohibitions remain visible in the source idea and require human review; the engine does not claim semantic negation detection.

A profile groups common signals into a conservative architecture recommendation:

- A browser-facing application receives an accessible responsive web-client baseline and a conventional HTTP application boundary.
- A developer or command-line tool receives a local-process baseline, explicit input/output contracts, actionable exit statuses, and cross-platform filesystem guidance.
- An otherwise unclassified idea receives a generic application baseline and an assumption asking the owner to confirm its delivery surface.

Profile names describe rules, not certainty. The generated rationale identifies which input signal selected a recommendation.

## Defaults

When an idea omits details, VibeSpec uses reviewable defaults rather than inventing product-specific facts:

- English is the initial product language.
- Accessibility, security, observability, testing, and documentation are required quality concerns.
- Data minimization and least privilege apply whenever stored or user-related data is inferred.
- Performance targets are framed as proposed measurable targets to validate, not guaranteed facts.
- External integrations, native mobile applications, complex billing, and multi-region operation remain out of scope unless the idea explicitly requires them.
- Ambiguous business rules are captured as assumptions or risks and assigned a validation task.

The exact emitted defaults are versioned with the package and covered by deterministic tests.

## Requirements and task derivation

Each recognized capability maps to a stable set of functional requirements and error/edge states. Cross-cutting non-functional requirements are included for supported platforms, performance, security, reliability, accessibility where relevant, and maintainability.

Tasks are emitted in dependency order. Every task has a stable identifier, one accountable role, dependencies, a bounded deliverable, and verifiable acceptance criteria. Shared contracts and architecture precede implementation; implementation precedes integration and end-to-end verification. Independent tasks at the same dependency level may run in parallel.

Acceptance criteria are repeated in a dedicated view so product owners and QA agents can verify outcomes without interpreting implementation tasks. Generated agent instructions constrain roles to the agreed specification and require escalation when an assumption would materially change scope.

## Non-inference guarantees

VibeSpec does not claim to determine market demand, legal compliance, final capacity needs, budgets, delivery dates, organization-specific standards, or the correctness of an unstated business rule. It does not silently choose a paid service or transmit idea content. Generated recommendations are a planning baseline, not professional legal or security advice.

## Adding or changing a rule

1. State the signal, precedence, emitted fields, and fallback explicitly.
2. Keep the transformation side-effect-free and stable.
3. Add positive, negative, overlap, and casing tests.
4. Verify the new rule does not reorder unrelated output.
5. Update example output expectations and user documentation if behavior is visible.
6. Record a changelog entry when a release changes generated bytes or manifest semantics.

Avoid fuzzy scores whose thresholds cannot be explained. If a more sophisticated provider is introduced later, it belongs behind a separately selected engine interface and must not make the offline engine depend on it.
