---
name: assess-skill-improvements
description: Use when the owner explicitly requests a manual evidence-based assessment of issues for skill improvements.
---

# Assess Skill Improvements

Run only on an explicit owner request, never automatically after delivery or acceptance. This
is analysis, not permission to edit skills, create a PR, or change tracker state. Use the
project's declared tracker and [track-open-issue](../track-open-issue/SKILL.md) for target,
capability, authentication, scoped authority and readback rules. If the declared owner is not
GitHub or the target/capability is unavailable, report the affected operation and corrective
action; do not invent a target or local ledger.

## Discover and select

Resolve and confirm the declared qualified GitHub host/owner/repository; verify `gh`, host
authentication and issue-read access as in track-open-issue. Discover all pages, not search
results or an open-only list:

```sh
gh api --method GET --hostname "$HOST" --paginate \
  "repos/$OWNER/$REPO/issues?state=all&per_page=100"
```

Exclude records containing `pull_request`. Inspect all pages of repository labels as well
as all relevant pages of comments for selected issues, and read available linked artifacts
and supported commits. A failed or inaccessible page is incomplete discovery or evidence,
not an empty result; report what was read and what remains. Allow explicit owner repository
or issue selection; do not silently sample matches. By default select unassessed issues:
those with none of the assessment state labels, whether open or closed, accepted or not.
An explicit reassessment may select already labelled issues. Record acceptance or its absence
as evidence, never as an eligibility filter.

Reuse equivalent existing assessment labels when available. Otherwise propose these three
labels, without creating them absent scoped tracker write authority:

- `skill-assessment:proposed`: evidence-backed proposal presented; implementation not claimed.
- `skill-assessment:no-change`: assessment delivered with rationale, including uncertainty or
  insufficient evidence where applicable.
- `skill-assessment:addressed`: approved improvement actually delivered, with exact
  implementation and verification evidence linked to that source issue.

## Reason and present

For each selected issue, distinguish original intent, available approved source and tasks,
feedback and correction effects, changed/new requirements, supported planning/task/
implementation/review omissions, and unnecessary workflow complexity. Separate verified
observations and supported causes from hypotheses and uncertain attribution. Name missing
or inaccessible approval, acceptance, artifact, comment and commit evidence. Classify commits
by supported purpose and links; author, time, or a blind Git range cannot establish attribution.
An unrelated commit is not evidence of a skill failure. Missing acceptance or approval does not
exclude the issue. Do not infer that every correction needs a new rule.

Group supported common causes across issues into the smallest justified proposals for existing
responsible skill owners. Link every source issue, supporting evidence and existing planning or
delivery destination; distinguish local project learning from portable guidance. Route any
proposed changes through existing planning and implementation approvals. A PR requires its own
applicable authority. The assessment itself must not edit skills or launch a self-modifying loop.
Present no-change and uncertain conclusions honestly, including evidence gaps and next useful
investigation. If discovery or evidence is incomplete, identify affected conclusions as partial.

## Record only authorized results

Proposed and no-change are analysis, never addressed. Only mark a source issue addressed when
its own approved proposed change is actually delivered and linked to exact implementation and
verification evidence; approval alone is insufficient. With explicit target- and operation-scoped
tracker write authority, create/apply needed labels or comment on selected issues only. Preserve
unrelated labels and content; update only assessment labels. Inspect conflicting existing states
and issue trail first, and correct only with known current evidence and authority. Read back each
label/comment effect independently. If a write or readback fails or is uncertain, report the
partial result and inspect the actual issue/comments before any retry; never claim a complete
transition or blindly duplicate a comment. Without authority, present the analysis without writes.
No scanner, separate learning ledger, automatic acceptance trigger, or implicit PR is created.
