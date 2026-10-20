# Workflow monitor — current integration basis and reusable dependency research

**Status:** revised proposal. Current repository inspection baseline: `213d0a7`.
The corrected brief was read directly from the owner-specified `dull-swan` worktree; no merge was needed.
Historical research remains available in Git, but its runtime model and scratch setup are not authority.

## What the script actually supplies

| Source | Actual behavior → design consequence |
| --- | --- |
| `runtime/coherence_workflow/store.py` | Creates `execution_runs` and `execution_tasks`; task/run writes update latest state. No retained phase definition or append-only new-run history. Legacy `read_history` reads `wf_*`, not these new-run execution traces. Add minimal new-contract records; do not adapt old graph tables. |
| `engine.py` | Sequential task worker, checks, checkpoint, then fresh independent reviewer. Rejected review raises with commits retained; no automatic correction/rereview loop. Record actual boundaries; explicitly link separately approved correction runs. |
| `verification.py` | Actual optional command checks; failed command raises before successful-task details can retain the check list. Add per-check observations before failure propagation; never export command/output. No PythonAnswer/deadline/catalog required. |
| `pi_adapter.py` | Optional observer callback exceptions are swallowed; questions use terminal input and send answers to host. Neither callback delivery nor stderr is durable history. Wrap coarse question milestones, not private SDK event streams. |
| `cli.py` / `intake.py` | Six task-linter checks; dependencies sort ordinary tasks; optional context survives. New status reads raw progress, not browser-safe DTOs. Additive metadata cannot become another startup validator. |
| `git_effects.py` | Real focused checkpoint or explicit no_change baseline/head; normal hooks/signing. Record the result rather than invent a receipt or equate no change with a new commit. |
| Runtime operating/schema guides | No graph/effect admission, catalog, host manifest, cgroup requirement or universal transport cap. Preserve ordinary writer ownership, actual checks, permissions and historical rows. |

Existing checks run during this revision's investigation:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests \
  .pi/workflow-validation/venv/bin/python -B -m unittest -v \
  test_engine test_pi_adapter test_recovery test_verification
```

**33 passed.** These existing tests exercise real disposable Git/check/process behavior and labelled
offline SDK transports. They confirm ordering, failed checks, review rejection, terminal input, large
transport results, optional-observer noninterference and legacy preservation. They do not implement
monitor recording, certify a live provider or establish application acceptance.

## Consequential choices

- **Selected:** retained descriptive phase inventory + append-only boundary observations. Without it,
  latest-state rows cannot support the intended graph/history. A task-status list is insufficient.
- **Rejected:** restore retired workflow runtime/YAML, trace proofs or broad SDK telemetry. These add
  machinery/privacy exposure without supplying a necessary product behavior.
- **Preserved:** explicit model execution nodes for rejected reviewer, fixing worker and rereviewer,
  with actual range/status history. Linked fresh correction runs avoid a new scheduler.
- **Necessary supporting change proposed:** optional actual review-base selection for full-original-range
  rereview. Current engine always starts review at its own run baseline; declaring a relationship alone
  cannot make a correction-only review cover earlier work. This small operational option needs explicit
  implementation approval, not just recording labels. Default execution semantics remain unchanged.
- **Privacy:** record only closed facts/public-safe presentation; no transcript mining or raw status
  forwarding. Missing presentation means generic label, not unreviewed task prose.

## Reusable library choices and official references

Retain earlier agent-selected React/React Flow + ELK and Starlette/Uvicorn proposals, originally chosen
under owner-delegated established-use/documentation criteria. They are not new owner package mandates.
The historical research recorded React/DOM19.3.1, @xyflow/react12.12.0, elkjs0.12.0, Vite8.3.4,
Starlette1.9.0/Uvicorn0.54.0 and Playwright1.64.1. These are **historical candidate versions**, not a
claim the current environment supplies them. Conventional compatible manifests/locks, relevant package
metadata/API/license/advisory checks and explicit setup approval replace forensic tree custody.
No new network research, dependency installation or app launch occurred in this revision.

| Reference | Applicable guidance and check |
| --- | --- |
| [React Flow layout](https://reactflow.dev/learn/layouting/layouting), [accessibility](https://reactflow.dev/learn/advanced-use/accessibility), [testing](https://reactflow.dev/learn/advanced-use/testing) | Interaction and layout are separate. Use stable IDs, measured DOM nodes, selectable/focusable nodes/edges, no connect/delete/editor handlers. Browser test real edges/navigation, not screenshot-only claims. |
| [React Flow props](https://reactflow.dev/api-reference/react-flow), [subflows](https://reactflow.dev/learn/layouting/sub-flows) | Disable editing, retain pan/zoom/selection. If grouping, parent before children and relative coordinates. Grouping never establishes task ownership. |
| [ELK README](https://github.com/kieler/elkjs), [layered algorithm](https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-layered.html) | Layout on a topology copy, preserve original edge endpoints/types despite cycle handling; local worker, discard stale generations. Re-layout only when needed, not every poll. Preserve notices/attribution. |
| [Vite build](https://vite.dev/guide/build.html), [assets](https://vite.dev/guide/assets.html) | Production local assets/worker, no HMR/CDN/sourcemaps exposed. Normal build output/locks, no external source-copy binding protocol. Check actual chosen version's Node requirements. |
| [React DOM common props](https://react.dev/reference/react-dom/components/common), [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent) | Inert text only, no dangerouslySetInnerHTML/stored URLs/styles/components. Test malicious stored labels and all response surfaces. |
| [Playwright assertions](https://playwright.dev/docs/test-assertions), [browsers](https://playwright.dev/docs/browsers) | Local installed browser/tool under approved setup; no automatic downloads or private profile reuse. Await observation assertions, never retry execution effects. |
| [Starlette routing](https://www.starlette.io/routing/), [responses](https://www.starlette.io/responses/), [exceptions](https://www.starlette.io/exceptions/), [Uvicorn settings](https://www.uvicorn.org/settings/) | Closed GET routes, explicit minimized DTOs, debug/reload/proxy/access-log leakage off. JSON serialization is not sanitization. Test actual500 response and log paths. Verify APIs at delivered locked versions. |
| [SQLite URI](https://www.sqlite.org/uri.html), [WAL](https://www.sqlite.org/wal.html), [Python sqlite3](https://docs.python.org/3/library/sqlite3.html) | mode=ro, short parameterized snapshots, normal locking and safe sidecars. No immutable/nolock/checkpoint/DDL. Closed-WAL retrospective read may need normal SQLite sidecar bookkeeping; don't forbid it categorically. |
| [Fetch Metadata](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site), [CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy) | Numeric-loopback exact Host/origin, same-origin API fetch, no CORS/control methods; safe CSP local resources. These are origin defenses, not malicious-local-client authentication. |

Alternatives remain credible but are not a new research project: Cytoscape requires custom accessible
card/navigation work; hand-built SVG duplicates interaction/layout; FastAPI adds unneeded API surface;
stdlib HTTP requires bespoke web-boundary handling. No adoption metric implies security/correctness.

## Validation and residuals

Use focused production-helper tests, real isolated script emission/readback/concurrent readers, and
browser graph/privacy checks. No mandatory prototype or proof-report chain. Exact snapshot budgets,
wire caps and dependency-tree attestations are not product acceptance.

Historical SDK/SQLite advisory observations are not clearance of the current environment. Consult
`docs/open_issues.md` and actual selected versions for relevant exposure before delivery. Monitor must
not import/expose SDK package/auth/resource APIs or act as a database writer/checkpointer. Dependency
changes/remediation need their proper authority; no silent upgrade. Preserve license notices (including
React Flow attribution and applicable ELK obligations) during ordinary dependency/distribution review.

All implementation checks remain prospective. Historical scratch fixtures/setup, old launch failures,
source hashes and receipts are not current app evidence or grounds to recreate retired admission.
