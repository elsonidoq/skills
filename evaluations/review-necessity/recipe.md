# Review necessity comparison recipe

This is a structural reproduction attempt, not a historical replay. The parent performs the calls after the T001 checkpoint and independent review, in the [parent schedule](../../docs/plans/review-necessity-reproduction-tasks.md#two-list-execution-and-parent-schedule). The only changing instruction is the selected revision's `roles/coherence-reviewer.md` body. The packet is the entire supplied case; do not supply this recipe, the oracle, source, incident, correction, other-revision guidance or pass assurances to the reviewer. Apply the source's [Required review direction](../../docs/plans/review-necessity-reproduction-tinyspec.md#required-review-direction) when reviewing this delivery, not as additional baseline instructions.

## Owner-approved packet-only revision

After two inconclusive attempts sought nonexistent implementation files, the owner explicitly requested this patch and one reviewer-subagent launch. The packet now states that only the supplied planning specification/task is in scope. Its intentional supplement obligation, source facts and independent expectations are unchanged. Earlier observations remain inconclusive and are not baseline failures for this revised case.

For this revision, no file tools are needed. Both baseline and any candidate must use the same no-file-tools setup. The test-only `.pi/agents/review-necessity-packet-only.md` configuration wraps the unchanged baseline reviewer body with empty tools/extensions and no inherited project/global/skill context. It is invocation configuration, not a new reviewer policy. Verify its body against the selected revision before launch. If testing a candidate, replace only the selected revision's body and preserve the packet, oracle and invocation settings.

Launch a fresh `review-necessity-packet-only` subagent with model `openai-codex/gpt-6.1-sol:medium`, the complete packet text as its task, an empty case working directory, and file-only output bound outside that directory. Supply neither this recipe nor expectations. Record effective tools and inspect observable events; do not infer absence of file access merely from configuration. Native subagent report-routing instructions are an invocation difference from the earlier CLI attempts and must remain equivalent for any candidate. Freeze the revised identities before this launch.

The CLI recipe below provides an equivalent no-tools invocation when explicitly selected; do not silently switch between CLI and native subagent for a previous/candidate pair.

## Before baseline

In the same retained checkout used for both coordinator launches, set `ROOT` to its absolute project root. The following uses bash, Git, Python 3 and installed Pi. Freeze the packet, expectations and recipe identities **before** baseline, and record their hashes in the observation. Preserve these files unchanged through comparison and acceptance. Inspect `pi --help` and installed settings/system additions for the current environment; `--no-context-files` does not disable global `SYSTEM.md` or `APPEND_SYSTEM.md`. Both must be absent or inspected and unchanged, with no answer or other-revision guidance. Check symlink targets, settings and any actual reads for contamination. Use the same environment and Pi version for both calls. Do not expose credentials in evidence.

```bash
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
sha256sum evaluations/review-necessity/{packet,expectations,recipe}.md
pi --version
pi --offline --list-models gpt-6.1-sol
pi auth check --provider openai-codex --model gpt-6.1-sol --no-refresh
```

The offline catalogue and non-refreshing auth check establish local readiness only, not provider callability or behavioral success. If the exact binding or necessary interface is unavailable, report the exact gap as **UNAVAILABLE** and do not substitute, install or authenticate. Check live readiness again at use if it may have changed. A call failure is inconclusive, not a behavioral result.

## Run once per revision

Run baseline with `REV=bad3ccc49ce491db3de990d2a4e638191176269a` and `LABEL=baseline`. Run candidate only after the valid miss and T002 checkpoint/review, with `REV` set to the explicit candidate commit SHA and `LABEL=candidate`. Resolve and record the full commit SHA and extracted body hash. Each invocation creates a separate empty working directory and separate output files under the retained project root. Do not run twice to force a result. Ensure the directory does not already exist; do not overwrite existing evidence. No file tools are supplied in this packet-only case. Actual oracle or cross-version intake still invalidates the run.

```bash
# Set REV and LABEL as directed above before running this block.
set -o pipefail
cd "$ROOT"
REV=$(git rev-parse --verify "${REV}^{commit}") || exit 1
OUT="$ROOT/.local/review-necessity/$LABEL"
mkdir -p "$ROOT/.local/review-necessity"
mkdir "$OUT" || exit 1
mkdir "$OUT/cwd" || exit 1
# Strip exactly the YAML frontmatter; the remaining body is the selected revision's resource.
git show "$REV:roles/coherence-reviewer.md" | python3 -c '
import sys
s = sys.stdin.read()
p = s.split("---\n", 2)
if len(p) != 3 or p[0] != "" or not p[2].strip():
    sys.exit("Invalid reviewer frontmatter/body")
sys.stdout.write(p[2])
' > "$OUT/reviewer-body.md" || exit 1
sha256sum "$OUT/reviewer-body.md"
printf 'revision: %s\n' "$REV"
# Command substitution removes trailing newlines only; no metadata or other role is supplied.
(cd "$OUT/cwd" && pi --offline --mode json --no-session --no-approve \
  --no-context-files --no-extensions --no-mcp --no-prompt-templates --no-themes \
  --no-skills --no-tools --provider openai-codex --model gpt-6.1-sol --thinking medium \
  --system-prompt "$(< "$OUT/reviewer-body.md")" \
  "$(< "$ROOT/evaluations/review-necessity/packet.md")") \
  > "$OUT/events.jsonl" 2> "$OUT/errors.txt"
STATUS=$?
printf 'exit status: %s\n' "$STATUS"
```

`--system-prompt` replaces Pi's default prompt; Pi can still append global system additions. `--no-session` creates fresh in-memory context and the disabled discovery flags prevent ordinary project/skill/extension intake. The body is supplied directly as text and the packet as the user message, not via the output directory or the oracle. Verify startup diagnostics, actual public tool calls/results and the final event; exit zero alone does not establish completion or full inspection. Inspect relevant environment differences and actual reads, including symlink targets. Preserve public evidence without private reasoning or credentials. Do not treat truncated, errored or incomplete observations as clean reviews.

## Parent observation and decision

After baseline and **before** any correction launch, write sanitized [source A1 comparison evidence](../../docs/plans/review-necessity-reproduction-tinyspec.md#red--inspect--minimal-fix--same-input-green) to `.local/review-necessity/baseline-observation.md` relative to this retained checkout. Include frozen identities, baseline revision and loaded body, Pi version, model/effort, invocation and relevant environment, completion/errors, actual public output/reads and expectation-based verdict with supporting quotes. Keep any linked public evidence under `.local/review-necessity/` with resolvable relative links so T002 can read it; no temporary-only evidence. Keep it outside Git and reviewer input.

A valid miss releases T002. A pass means **not reproduced** and correction/candidate **NOT RUN**; incomplete/error or actual contamination is **inconclusive**, also no correction/candidate. Never retry to force red. After a justified candidate checkpoint and independent review, run the same recipe once with the candidate SHA. Record A1 candidate evidence referencing the baseline observation and interpret per source A4: fail/pass is improvement on this case only; fail/fail unresolved; errors/incomplete observations inconclusive. Overall acceptance also requires fresh independent acceptance review; static readiness is not behavioral green.
