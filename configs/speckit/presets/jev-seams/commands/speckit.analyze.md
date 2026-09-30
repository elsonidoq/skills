## Optional Jev-on advisory analysis ranking

Use this append guidance only when **Jev-on mode** is active, the instrumented tools are available, and complete deterministic inventories already exist. Form an explicit set of **2 to 50** likely requirement-task associations and low-risk cross-artifact findings with stable opaque IDs. Retain the complete deterministic inventories and all original evidence outside telemetry.

Only `jev_rank` is the measured Jev interface; never use raw shell or MCP Jev. Do not send credentials, secrets, personal data, or unauthorized sensitive payloads. Ask `jev_rank` only to rank priority for deeper inspection. It cannot dismiss a finding, score a constitution conflict away, set constitution-conflict severity, or decide coverage or correctness.

The main agent verifies all coverage, severity, conflicts, and constitution alignment from the complete inventories. Record `jev_disposition` for each reviewed proposal as accepted, overridden, or not used; proposals without a disposition remain pending. If Jev-on is absent or `jev_rank` returns no proposals, use the unchanged manual workflow.

Preserve complete inventories and the command's read-only behavior.
