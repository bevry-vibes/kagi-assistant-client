# kagi-assistant-client

API client and crawler for [Kagi Assistant](https://assistant.kagi.com) conversations: fetch public share exports and (with your session cookie) your own conversations, branches, and full message histories — as Markdown or JSON.

## Install

```sh
pip install .
# or run directly: python3 kagi_assistant.py ...
```

## Usage

```sh
# public share exports (no auth needed)
kagi-assistant share <share-uuid>                 # markdown transcript
kagi-assistant share <share-uuid> --format json   # raw json

# your own conversations (auth required)
export KAGI_SESSION="<your kagi_session cookie>"
kagi-assistant conversation <conversation-uuid>   # metadata + branches
kagi-assistant branches <conversation-uuid>       # branch list
kagi-assistant messages <branch-uuid>             # full transcript (markdown)
kagi-assistant messages <conversation-uuid>       # resolves to the first branch
```

`KAGI_SESSION` is read from the environment only — never stored, never committed. Keep it in your shell profile or a `.env` file (`.env` is gitignored).

## API endpoints used

Discovered against `assistant.kagi.com` (2026-08-11):

| Endpoint | Auth | Notes |
|---|---|---|
| `GET /api/shares/<uuid>` | no | share export: `{conversation, messages}` |
| `GET /api/conversations/<uuid>` | yes | metadata + branches |
| `GET /api/conversations/<uuid>/branches` | yes | branch list |
| `GET /api/branches/<uuid>/messages` | yes | default page 25 — pass `?limit=100`; paginate with `?before=<oldest-uuid>` and dedup by uuid |

<!-- LICENSE/ -->

## License

Unless stated otherwise all works are:

- Copyright &copy; [Benjamin Lupton](https://balupton.com)

and licensed under:

- [Reciprocal Public License 1.5](http://spdx.org/licenses/RPL-1.5.html)

<!-- /LICENSE -->
