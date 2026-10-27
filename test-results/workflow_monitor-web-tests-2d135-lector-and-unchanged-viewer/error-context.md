# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow_monitor/web/tests/test_multiproject.spec.ts >> actual CLI capture survives fixture source removal through ordinary project selector and unchanged viewer
- Location: workflow_monitor/web/tests/test_multiproject.spec.ts:46:1

# Error details

```
Error: browserType.launch: Executable doesn't exist at /home/dev/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell
╔════════════════════════════════════════════════════════════╗
║ Looks like Playwright was just installed or updated.       ║
║ Please run the following command to download new browsers: ║
║                                                            ║
║     npx playwright install                                 ║
║                                                            ║
║ <3 Playwright Team                                         ║
╚════════════════════════════════════════════════════════════╝
```