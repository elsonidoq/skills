## Optional Jev-on advisory task-association ranking

Use this append guidance only when **Jev-on mode** is active, the instrumented tools are available, and named entities or interface contracts have a complete inventory. Form an explicit set of **2 to 50** likely user-story matches with stable opaque IDs. Retain the complete entity and interface-contract inventory and all original coverage evidence outside telemetry.

Only `jev_rank` is the measured Jev interface; never use raw shell or MCP Jev. Do not send credentials, secrets, personal data, or unauthorized sensitive payloads. Ask `jev_rank` only to rank likely user-story matches for the named entity or interface contract. It cannot generate tasks, assign stories, reorder dependencies, or determine completeness.

The main agent assigns stories, designs tasks, orders dependencies, and preserves complete coverage. Record `jev_disposition` for each reviewed proposal as accepted, overridden, or not used; proposals without a disposition remain pending. If Jev-on is absent or `jev_rank` returns no proposals, use the unchanged manual workflow.

Complete coverage and valid dependency order remain mandatory.
