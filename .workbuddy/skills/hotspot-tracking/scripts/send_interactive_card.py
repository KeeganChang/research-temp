#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send a Feishu interactive card to a group via lark-cli.

Why this script exists
----------------------
`lark-cli im +messages-send --content` accepts ONLY an inline JSON string in
this version. Neither `--content @file` nor `--content -` (stdin) works, and a
~5KB card contains Chinese text plus single quotes that cannot be safely passed
through shell quoting. This script bypasses the problem by invoking node
directly with the card JSON as a subprocess *list argument* (no shell, no
quoting). It also calls the managed node binary directly, skipping the
flaky `exec node` layer inside the lark-cli bash wrapper.

Usage
-----
    .venv/Scripts/python.exe scripts/send_interactive_card.py \
        --chat-id oc_xxx --card card.json --key hotspot-20260924-a [--as user]
"""
import argparse
import json
import subprocess
import sys

# Managed node binary (bypass the lark-cli bash wrapper's flaky `exec node`).
NODE = r"C:\Users\hello\.workbuddy\binaries\node\versions\22.22.2-6\node.exe"
RUN_JS = (
    r"C:\Users\hello\.workbuddy\binaries\node\cli-connector-packages"
    r"\node_modules\@larksuite\cli\scripts\run.js"
)


def main():
    ap = argparse.ArgumentParser(description="Send a Feishu interactive card.")
    ap.add_argument("--chat-id", required=True, help="target chat/group id")
    ap.add_argument("--card", required=True, help="path to Card 2.0 JSON file")
    ap.add_argument(
        "--key", required=True,
        help="idempotency key (prevents duplicate send on retry)",
    )
    ap.add_argument(
        "--as", dest="identity", default="user", choices=["user", "bot"],
        help="send identity (default: user)",
    )
    args = ap.parse_args()

    with open(args.card, encoding="utf-8") as f:
        card = f.read()

    # Fail fast on malformed card JSON.
    try:
        json.loads(card)
    except json.JSONDecodeError as e:
        sys.exit("CARD JSON INVALID: " + str(e))

    cmd = [
        NODE, RUN_JS, "im", "+messages-send",
        "--chat-id", args.chat_id,
        "--msg-type", "interactive",
        "--content", card,
        "--idempotency-key", args.key,
        "--as", args.identity,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    sys.stdout.write("EXIT=%d\n" % r.returncode)
    sys.stdout.write(r.stdout)
    if r.stderr.strip():
        sys.stdout.write("\nSTDERR:\n" + r.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
