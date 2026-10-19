# F1 affected rereview

**Verdict: READY FOR OWNER REVIEW of the corrected planning scope. Not ready for runtime admission.**

Reviewed `db6a8f0..f16a6363dea1a9a73fbb3b25964f6a556a948981`, the producer return and actual affected artifacts. **F1 is resolved at planning level. No new blocking regression identified.**

## F1 disposition

- **Unsupported setup courier removed:** `tasks.md:21–25,45–48` and `contracts/validation.md:34` now explicitly prohibit routine setup through question/answer delivery. Genuine question categories remain unchanged.
- **Supported replacement specified:** `contracts/validation.md:36–41` defines separately authorized pre-admission dependency setup, reviewable immutable external inputs, fixed inherited `TMPDIR/monitor-inputs.json`, same-byte hash validation and real-store reobservation. This fits actual PythonAnswer environment/ownership semantics (`runtime/coherence_workflow/cli.py:51–63`) without new tools or runtime changes.
- **Independent expected identity, no hash cycle:** `contracts/validation.md:38–40` obtains the descriptor’s expected hash from source-pinned quickstart, checks actual `wf_run_inputs`/bindings and excludes reverse task/approval hashes. `quickstart.md:16–21` honestly leaves both launch pins unresolved and requires renewed current-content binding before launch.
- **Application custody preserved:** `contracts/validation.md:41` retains in-run worker production/full review of manifests, app source and helpers. Only third-party locks/dependency trees become external admitted inputs. Scratch builds copy current owned source with bound hashes; they do not substitute prebuilt application code or authorize worktree generation.

The recipe is sufficiently concrete for the implementer. Actual immutable custody, helper correctness, dependency compatibility and bounded checks remain future proofs—not established results.

## Preserved review conclusions

Previous **17-FR/six-SC coverage**, four sequential outcomes/eight REQUIRED mappings and precursor proportionality stand. Check IDs/versions/arguments, dependencies, evidence mappings, executor intent, same-build retrospective/live requirements and independent final acceptance remain intact. Precursor JSON changes only three source hashes.

**Static verification PASS:** both schemas, all current source hashes, five canonical action scopes/effects, unchanged check identities and dependencies, obsolete-lock-only ownership removal, precursor non-hash equivalence and whitespace checks. Seven changed paths; final worktree/index clean at expected HEAD.

Four checkout-local skill paths/hashes still match. Selected and environment-observed profile remains `openai-codex/gpt-6.1-sol:medium`; provider acknowledgement unknown. No tests, installs, network, browser, runtime or model launches performed.

## Remaining admission gates

Owner review does not approve nonexistent launch values. Execution still requires explicit precursor scope/mode approval and verified independent acceptance; authorized real dependency/custody setup; actual descriptor/run pins; refreshed source hashes/scopes and affected current-content review/owner/catalog approval; usable SDK/resources/containment; and all real REQUIRED evidence. SDK OI-3/SQLite residuals remain retained.