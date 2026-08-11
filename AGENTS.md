# AGENTS

Before working on this project, read and follow these remote skills (do not copy them in; reference their canonical locations):

- [policy.md](https://github.com/bevry-vibes/skills/blob/master/policy.md) — Bevry's AI policy: which agents are permitted to work on this project.
- [commits.md](https://github.com/bevry-vibes/skills/blob/master/commits.md) — commit hygiene: Conventional Commits, author vs co-author identity, verification.
- [minimax.md](https://github.com/bevry-vibes/skills/blob/master/minimax.md) — MiniMax model tweaks.

## Project

`kagi_assistant.py` is a stdlib-only Python client + CLI for Kagi Assistant's API (see the README's endpoint table). Keep it dependency-free. The session token is read from `KAGI_SESSION` only and must never be committed — `.env` is gitignored; check `git grep` before committing anything that touched credentials.
