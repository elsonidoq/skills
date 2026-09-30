# Installation and Activation Contract

## Modes

### Manual mode (default)

- Installs and exposes the existing suite workflows.
- Does not require Jev, authentication, the metrics extension, or SpecKit.
- Does not enable Jev seam instructions and does not claim measured Jev use.
- Missing Jev/tracker capability is a normal manual-mode state, not an installation error.

### Jev-on mode (explicit opt-in)

A Jev-on request is transactional. No optimized seam is enabled until every requested component
passes preflight and the tracker is activated.

## Required preflight

For the global-suite seams:

1. Pi version is compatible with the extension API used by the tracker (tested baseline: 0.87.1;
   accepted release line: 0.87.x only until compatibility tests prove another line).
2. Node runtime supports the extension's JavaScript level and built-in test runner.
3. The Jev metrics extension and its pure modules load successfully in the local preflight harness.
4. The extension registers `jev_rank`, `jev_disposition`, `jev_metrics`, and `/jev-metrics` against a
   fake ExtensionAPI without duplicate names or startup errors.
5. `jev --version` succeeds with a supported response contract (tested baseline: `jev-cli` 0.6.3).
6. `jev auth test` succeeds for the configured provider. This is an explicit network prerequisite
   check initiated by selecting Jev-on mode; it sends only Jev's fixed authentication-test payload,
   never repository candidates.
7. Deterministic extension and installer tests pass.

For SpecKit seams in a target project, additionally:

8. The target has project-local SpecKit commands, scripts, and a live constitution.
9. Its preset resolver supports an append layer over all four core commands.
10. The target integration can regenerate and introspect composed command artifacts.

A failed check reports:

- the missing or incompatible prerequisite,
- the observed version/status without credential material,
- the action needed to resolve it, and
- confirmation that no optimized seam was enabled.

## Activation order

1. Stage extension and optional SpecKit preset artifacts without changing active paths.
2. Complete preflight.
3. Activate the Pi extension/tracking tools.
4. Verify the active runtime/resource path resolves the tracker.
5. Activate the four global skill seam instructions.
6. If requested, install/reconcile the project-local SpecKit preset and verify all four composed
   commands.
7. Report activation and require `/reload` because global configuration-time assets changed.

If any activation step fails, restore the pre-activation paths/registry and report rollback status.
Partial seam activation is an installation failure.

## SpecKit override distribution

The distributable source is a preset with four `strategy: append` command layers:

- `speckit.analyze`
- `speckit.checklist`
- `speckit.clarify`
- `speckit.tasks`

Installation materializes it under the target project's `.specify/presets/` registry and uses the
installed SpecKit reconciliation command to produce integration prompts. It must not hand-edit,
search/replace, or checksum-patch `.pi/prompts/speckit.*.md`.

Verification requires both:

- resolver/introspection evidence naming the project preset as an active layer for each command; and
- generated command inspection showing the complete core workflow plus exactly one bounded Jev seam
  addition.

An incompatible target keeps all four SpecKit seams disabled. Installing only a subset is not
allowed in the initial feature.

## Non-Jev fallback

When Jev-on mode was not selected, every modified global skill and SpecKit override must guard use of
the instrumented tools. If the guard is not met, the original manual instructions execute unchanged.
No raw shell or MCP Jev call substitutes for the tracker.

Once Jev-on is active, a per-invocation Jev failure still returns the complete candidate set to the
main agent for manual handling and records a tracked non-success. Installation strictness does not
turn a transient runtime failure into silent candidate loss.

## Rollback

Rollback disables/removes the active tracker resource and project preset registration, reconciles
SpecKit prompts from remaining layers, and restores manual workflows. It preserves Pi session entries
and CSV history. Deleting persisted metrics, uninstalling Jev, or changing provider credentials is
outside automatic rollback and needs explicit user action.
