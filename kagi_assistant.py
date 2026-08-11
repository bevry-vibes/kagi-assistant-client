#!/usr/bin/env python3
"""kagi-assistant — API client and crawler for Kagi Assistant conversations.

Endpoints (discovered 2026-08-11 against assistant.kagi.com):

- GET /api/shares/<uuid>                   public share export (conversation + messages)
- GET /api/conversations/<uuid>            conversation metadata + branches (auth)
- GET /api/conversations/<uuid>/branches   branch list (auth)
- GET /api/branches/<uuid>/messages        branch messages (auth); default page is 25 —
                                           pass ?limit=100; paginate with
                                           ?before=<oldest-uuid> and dedup by uuid

Authentication: the KAGI_SESSION environment variable (your `kagi_session`
cookie from kagi.com). Only the share endpoint works without it.

Usage:
    kagi-assistant share <share-uuid> [--format md|json]
    kagi-assistant conversation <conversation-uuid>
    kagi-assistant branches <conversation-uuid>
    kagi-assistant messages <branch-uuid | conversation-uuid> [--format md|json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://assistant.kagi.com/api"
USER_AGENT = "kagi-assistant-client/0.1 (+https://github.com/bevry-vibes/kagi-assistant-client)"


def _request(path: str, session: str | None) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            **({"Cookie": f"kagi_session={session}"} if session else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit(
                "error: not_authenticated — set the KAGI_SESSION environment variable "
                "to your kagi_session cookie."
            )
        sys.exit(f"error: HTTP {e.code} for {path}: {e.read()[:200]!r}")


def get_session(required: bool) -> str | None:
    session = os.environ.get("KAGI_SESSION", "").strip()
    if required and not session:
        sys.exit("error: KAGI_SESSION environment variable is required for this command.")
    return session or None


def fetch_share(share_uuid: str) -> dict:
    """Fetch a public share export: {conversation, messages}."""
    return _request(f"/shares/{share_uuid}", get_session(required=False))


def fetch_conversation(conversation_uuid: str) -> dict:
    return _request(f"/conversations/{conversation_uuid}", get_session(required=True))


def fetch_branches(conversation_uuid: str) -> list:
    data = _request(
        f"/conversations/{conversation_uuid}/branches", get_session(required=True)
    )
    return data.get("branches", data if isinstance(data, list) else [])


def fetch_branch_messages(branch_uuid: str, limit: int = 100) -> list:
    """Fetch all messages of a branch, paginating with the `before` cursor and
    deduplicating by uuid (the default page is 25; limit=100 usually suffices)."""
    session = get_session(required=True)
    seen: dict[str, dict] = {}
    before = None
    for _ in range(20):
        query = f"?limit={limit}" + (f"&before={before}" if before else "")
        data = _request(f"/branches/{branch_uuid}/messages{query}", session)
        box = data.get("messages", data)
        items = box.get("items", box if isinstance(box, list) else [])
        has_more = box.get("has_more", False) if isinstance(box, dict) else False
        new = [m for m in items if m.get("uuid") not in seen]
        for m in new:
            seen[m["uuid"]] = m
        if not items or not has_more or not new:
            break
        items.sort(key=lambda m: m.get("created_at", ""))
        before = items[0].get("uuid")
        time.sleep(0.3)
    return sorted(seen.values(), key=lambda m: m.get("created_at", ""))


def to_markdown(title: str, messages: list) -> str:
    out = [f"# {title}"]
    for m in messages:
        out.append(f"\n--- [{m.get('role', '?')}] ---\n\n{m.get('content') or ''}")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(prog="kagi-assistant", description=__doc__)
    parser.add_argument(
        "--format", choices=["md", "json"], default="md", help="output format (default: md)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("share", help="fetch a public share export").add_argument("uuid")
    sub.add_parser("conversation", help="fetch conversation metadata + branches").add_argument(
        "uuid"
    )
    sub.add_parser("branches", help="list a conversation's branches").add_argument("uuid")
    sub.add_parser(
        "messages",
        help="fetch all messages of a branch (or of a conversation's first branch)",
    ).add_argument("uuid")
    args = parser.parse_args()

    if args.command == "share":
        data = fetch_share(args.uuid)
        if args.format == "json":
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(to_markdown(data["conversation"]["title"], data["messages"]))
    elif args.command == "conversation":
        print(json.dumps(fetch_conversation(args.uuid), indent=2, ensure_ascii=False))
    elif args.command == "branches":
        print(json.dumps(fetch_branches(args.uuid), indent=2, ensure_ascii=False))
    elif args.command == "messages":
        uuid = args.uuid
        branches = fetch_branches(uuid)
        if branches:  # it was a conversation uuid; resolve to its first branch
            uuid = branches[0]["uuid"]
        messages = fetch_branch_messages(uuid)
        if args.format == "json":
            print(json.dumps(messages, indent=2, ensure_ascii=False))
        else:
            print(to_markdown(f"branch {uuid}", messages))


if __name__ == "__main__":
    main()
