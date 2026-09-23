# AGENTS.md

This project conforms to Bevry's skills.
Reference their remote URLs only — do not pull their contents into this file.
When a referenced skill applies with this project's tweaks, the local `<name>.md` file at this repo root references the remote URL and lists the tweaks underneath;
this process is documented in the upstream repo's [local tweaks pattern](https://github.com/bevry-vibes/skills#local-tweaks-pattern).

- https://github.com/bevry-vibes/skills/blob/main/policy.md — **applies.** Bevry's AI policy, mandating which AIs are permitted
- https://github.com/bevry-vibes/skills/blob/main/commits.md — **applies.** Commit hygiene: Conventional Commits, author vs co-author identity, verification
- https://github.com/bevry-vibes/skills/blob/main/python.md — **applies.** All Python setup and execution through uv; stdlib first, a dependency only when the stdlib cannot do the job
- https://github.com/bevry-vibes/skills/blob/main/minimax.md — **applies** when the running agent is a MiniMax M3 model (its rules gate themselves on model and harness)

## Project

`kagi_assistant.py` is a stdlib-only Python client + CLI for Kagi Assistant's API (see the README's endpoint table). Keep it dependency-free. Python setup runs through uv only (`uv sync` / `uv run` / `uv tool install`; `uv.lock` and `.python-version` are committed). The session token is read from `KAGI_SESSION` only and must never be committed — `.env` is gitignored; check `git grep` before committing anything that touched credentials.
