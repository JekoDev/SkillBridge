---
name: skillbridge-auto-integrator
description: Integrate open-source SkillBridge into an existing codebase with a safe, reviewable, agent-assisted workflow. Use when the user asks to make their application discoverable or usable by AI agents.
---

# SkillBridge Auto Integrator

Make an existing app agent-ready using the open-source [SkillBridge](https://github.com/JekoDev/SkillBridge) framework. This skill guides a coding agent; it does **not** grant access to private application APIs or execute commands without permission.

## Phase 1: Inspect (no modifications)

1. Confirm the repository root and inspect the existing tests and auth model.
2. If SkillBridge v0.9+ with `inspect-project` is installed, run `python -m skillbridge.cli inspect-project .` (or `skillbridge inspect-project .`). If the command is unavailable, manually inspect top-level build files; do not claim it exists.
3. Identify language/runtime and existing public CLI, OpenAPI, MCP, or service entry points.
4. Propose 2-5 narrowly scoped capabilities with inputs, outputs, and read/write/destructive classification. **Ask the user to approve the capabilities before changing files.**

## Phase 2: Integrate (after approval)

1. Check the **installed version** and official source/examples at https://github.com/JekoDev/SkillBridge; never invent API names or manifest fields.
2. Prefer reusing an existing integration. Otherwise create a minimal adapter that calls the application's established public service layer with its existing authentication/authorization.
3. For current manifest-based command skills, use the actual documented `skillbridge.json` format: `app`, `skills`, and for each command skill `name`, `description`, `type: command`, `inputs`, `argv`. The current command interface accepts string, integer and boolean inputs; inspect the installed version before relying on these fields.
4. Avoid exposing shell, environment variables, arbitrary file reads, credentials, database administration or private user data. Never add a bypass for authentication.
5. Preserve existing application behavior. Keep modifications small and reviewable.

## Phase 3: Verify

1. Run `python -m skillbridge.cli inspect <manifest-folder>` to validate/discover the manifest; use the installed CLI help if syntax differs.
2. Run existing project tests. Test one harmless read-only capability. **Never enable command execution for verification without explicit user authorization.**
3. Explain how to start the adapter, connect an agent through the documented MCP stdio interface, grant permissions, and undo the integration.
4. Report exact changed files, tests executed and remaining limitations. Do not claim an integration works if not tested.

## Example interaction

User: "Make my mail app AI-agent ready."

Agent: "I found mail-list and mail-read service methods. I propose read-only `list_messages` and `read_message` capabilities. Sending mail is a write action and will stay disabled unless you approve it. Shall I integrate those two read-only capabilities?"

## Important security boundary

SkillBridge discovery is read-only. Its command execution is disabled by default and, when authorized, runs under the local OS user rather than inside a sandbox. Never treat manifest discovery as authorization to execute commands.

SkillBridge itself is MIT-licensed and free. This skill sells the convenience of a structured integration workflow, not exclusive rights to the framework.
