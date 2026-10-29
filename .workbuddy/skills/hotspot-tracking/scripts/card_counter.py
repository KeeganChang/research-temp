#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hotspot card interactive backend: like / click / vote / drill (zero-dependency).

Why this exists
---------------
The "A股近一周热点追踪" card shows the 研判 as its main body and appends
data-source links at the bottom. The user wants those links to support
**点赞 (like)** and **点击计数 (click count)**, plus a few richer interactions.
Feishu Card 2.0 has no native counter, so we implement a tiny stdlib backend:

  * 🔗 打开 -> `callback`(action=open) -> increments click_count, returns an
               `open_url` action so the real URL still opens.
  * 👍 赞   -> `callback`(action=like) -> increments like_count, returns
               `update_card` so the count refreshes in place.
  * 👍/👎 研判反馈 -> `callback`(action=vote) -> increments a vote, refreshes card.
  * 追一下   -> `callback`(action=drill) -> writes a queue row, toasts.

The server is plain stdlib (http.server + sqlite3). To make interactions live,
expose it publicly and point the Feishu app's Request URL (event subscription)
at `<public>/feishu/callback`. Then send the card with `lark-cli im +messages-send`.

The rendered card is built from `../assets/card_interactive_hotspot.json` (the
exact S2 layout the user confirmed) with live counters injected — so a refresh
after a like/open stays pixel-identical to the sent card.

Local validation (no public server needed):
    python card_counter.py --seed
    python card_counter.py --build-card --out /tmp/x.json
    python card_counter.py --serve --port 8787
    curl -X POST localhost:8787/feishu/callback -d '{"type":"url_verification","challenge":"abc"}'
    curl -X POST localhost:8787/feishu/callback -H 'Content-Type: application/json' \
      -d '{"event":{"type":"card.action.trigger","action":{"value":{"source_id":"src1","action":"like"}}}}'
    curl localhost:8787/stats
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import threading
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")
DB_PATH = os.path.join(DATA_DIR, "counter.db")
TEMPLATE_PATH = os.path.join(HERE, "..", "assets", "card_interactive_hotspot.json")

BASE_URL = os.environ.get("CARD_BASE_URL", "http://127.0.0.1:8787")

# Data sources backing the report (urls from the report frontmatter).
# Order / id MUST match the buttons in card_interactive_hotspot.json:
#   src1 -> 半导体/国产算力链 (eastmoney) · Tier2
#   src2 -> 光模块/CPO/1.6T    (toutiao)   · Tier3
#   src3 -> 人形机器人·特斯拉   (qq news)  · Tier3
# tier follows the report's 数据可信度 section: Tier1 官方/一手, Tier2 机构研报,
# Tier3 媒体转述.
SOURCES = [
    {
        "id": "src1",
        "title": "半导体 / 国产算力链（主升→分歧）",
        "source": "东方财富",
        "tier": "Tier2",
        "url": "https://finance.eastmoney.com/a/202609243883764051.html",
    },
    {
        "id": "src2",
        "title": "光模块 / CPO / 1.6T（高位回撤）",
        "source": "今日头条",
        "tier": "Tier3",
        "url": "https://www.toutiao.com/article/7687000465594139170",
    },
    {
        "id": "src3",
        "title": "人形机器人 · 特斯拉审厂（持续催化）",
        "source": "腾讯新闻",
        "tier": "Tier3",
        "url": "https://news.qq.com/rain/a/20260922A05C8500",
    },
]

# Verdict feedback votes and mainline poll options.
FEEDBACK_VOTES = [("v_useful", "👍 有用"), ("v_doubt", "👎 存疑")]
VOTE_KEYS = {k for k, _ in FEEDBACK_VOTES}

BASE_URL_FEISHU = "https://my.feishu.cn/base/GqZ8bhLL5aThICsG4bGcOnQIn6Z"
DOC_URL_FEISHU = "https://my.feishu.cn/docx/HjQ8dlqOYoVcHWxRcPQcnx9qnle"

# --- Base sync config -------------------------------------------------------
# Interaction totals (点赞数 / 点击数) are written back to the Feishu Base that
# already holds the signal sources. The Base is the 资讯域 SSOT (per AGENTS.md
# 铁律#2), so mirroring the live counters there keeps the shareable view in sync.
# NOTE: the node binary path is environment-specific (managed runtime), not a
# project path, so it is intentionally absolute here, consistent with
# send_interactive_card.py / lark_base_call.py.
BASE_TOKEN = "GqZ8bhLL5aThICsG4bGcOnQIn6Z"
TABLE_ID = "tbl0JYm0AstPfJeu"
LARK_NODE = r"C:\Users\hello\.workbuddy\binaries\node\versions\22.22.2-6\node.exe"
LARK_RUN = (
    r"C:\Users\hello\.workbuddy\binaries\node\cli-connector-packages"
    r"\node_modules\@larksuite\cli\scripts\run.js"
)
BASE_FIELD_LIKE = "点赞数"
BASE_FIELD_CLICK = "点击数"
SYNC_CFG = os.path.join(DATA_DIR, "base_sync.json")
_url_map = None  # url -> record_id, lazily built
_url_map_lock = threading.Lock()


def db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY, title TEXT, source TEXT, tier TEXT, url TEXT,
            like_count INTEGER DEFAULT 0, click_count INTEGER DEFAULT 0)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS votes (
            key TEXT PRIMARY KEY, count INTEGER DEFAULT 0)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, created_at TEXT)"""
    )
    return conn


def seed():
    conn = db()
    cur = conn.cursor()
    for s in SOURCES:
        cur.execute(
            """INSERT OR IGNORE INTO sources (id,title,source,tier,url)
               VALUES (?,?,?,?,?)""",
            (s["id"], s["title"], s["source"], s["tier"], s["url"]),
        )
    for k in sorted(VOTE_KEYS):
        cur.execute("INSERT OR IGNORE INTO votes (key,count) VALUES (?,0)", (k,))
    conn.commit()
    conn.close()
    print("seeded %d sources, %d vote keys" % (len(SOURCES), len(VOTE_KEYS)))


def get_rows():
    conn = db()
    rows = conn.execute(
        "SELECT id,title,source,tier,url,like_count,click_count FROM sources"
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "source": r[2], "tier": r[3], "url": r[4],
         "like": r[5], "click": r[6]}
        for r in rows
    ]


def get_votes():
    conn = db()
    rows = conn.execute("SELECT key,count FROM votes").fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def get_queue():
    conn = db()
    rows = conn.execute("SELECT id,label,created_at FROM queue ORDER BY id").fetchall()
    conn.close()
    return [{"id": r[0], "label": r[1], "created_at": r[2]} for r in rows]


def like_source(source_id):
    conn = db()
    conn.execute(
        "UPDATE sources SET like_count = like_count + 1 WHERE id = ?", (source_id,)
    )
    conn.commit()
    conn.close()


def click_source(source_id):
    conn = db()
    conn.execute(
        "UPDATE sources SET click_count = click_count + 1 WHERE id = ?", (source_id,)
    )
    conn.commit()
    conn.close()


def bump_vote(key):
    conn = db()
    conn.execute("UPDATE votes SET count = count + 1 WHERE key = ?", (key,))
    conn.commit()
    conn.close()


def enqueue(label):
    conn = db()
    conn.execute(
        "INSERT INTO queue (label,created_at) VALUES (?,?)",
        (label, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()


def real_url(source_id):
    conn = db()
    row = conn.execute("SELECT url FROM sources WHERE id = ?", (source_id,)).fetchone()
    conn.close()
    return row[0] if row else BASE_URL_FEISHU


# --- Base sync (点赞数 / 点击数 -> Feishu Base) -------------------------------

def _lark_base(args, timeout=20):
    """Run a lark-cli base command; return stdout string or None on failure."""
    cmd = [LARK_NODE, LARK_RUN] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", timeout=timeout)
        return r.stdout or ""
    except Exception as e:  # noqa: BLE001 - best-effort sync must never crash clicks
        print("[sync] lark call failed:", e)
        return None


def _extract_url(title):
    m = re.search(r"\]\(([^)]+)\)", title or "")
    return m.group(1) if m else None


def ensure_url_map():
    """Build url -> record_id from the Base, cache to SYNC_CFG. Thread-safe."""
    global _url_map
    with _url_map_lock:
        if _url_map is not None:
            return _url_map
        if os.path.exists(SYNC_CFG):
            try:
                cfg = json.load(open(SYNC_CFG, encoding="utf-8"))
                cached = cfg.get("url_map") or {}
                if cached:
                    _url_map = cached
                    return _url_map
            except Exception:
                pass
        url_map = {}
        out = _lark_base(["base", "+record-list", "--base-token", BASE_TOKEN,
                          "--table-id", TABLE_ID, "--as", "user", "--format", "json"])
        if out:
            try:
                d = json.loads(out).get("data", {})
                rows = d.get("data", []) or []
                rids = d.get("record_id_list", []) or []
                for i, row in enumerate(rows):
                    # column 0 = 标题 (contains the '[title](url)' markdown link)
                    title = row[0] if isinstance(row, list) and row else ""
                    uid = _extract_url(title)
                    rid = rids[i] if i < len(rids) else None
                    if uid and rid:
                        url_map[uid] = rid
            except Exception as e:
                print("[sync] parse record-list failed:", e)
        _url_map = url_map
        try:
            json.dump({"url_map": url_map}, open(SYNC_CFG, "w", encoding="utf-8"))
        except Exception:
            pass
        return url_map


def ensure_base_fields():
    """Create 点赞数 / 点击数 number fields if missing. Idempotent."""
    out = _lark_base(["base", "+field-list", "--base-token", BASE_TOKEN,
                      "--table-id", TABLE_ID, "--as", "user", "--format", "json"])
    existing = set()
    if out:
        try:
            d = json.loads(out)
            for f in d.get("data", {}).get("fields", []):
                existing.add(f.get("name") or f.get("field_name"))
        except Exception:
            pass
    for fname in (BASE_FIELD_LIKE, BASE_FIELD_CLICK):
        if fname in existing:
            print("[sync] field exists:", fname)
            continue
        _lark_base(["base", "+field-create", "--base-token", BASE_TOKEN,
                    "--table-id", TABLE_ID, "--as", "user",
                    "--json", json.dumps({"name": fname, "type": "number"},
                                         ensure_ascii=False)])
        print("[sync] created field:", fname)


def sync_to_base(source_id):
    """Best-effort push like/click counts to the matching Base record.
    Runs in a daemon thread so the card click returns instantly."""
    def _job():
        rows = [r for r in get_rows() if r["id"] == source_id]
        if not rows:
            return
        r = rows[0]
        url_map = ensure_url_map()
        rid = url_map.get(r["url"])
        if not rid:
            print("[sync] no base record mapped for", source_id, r["url"])
            return
        payload = json.dumps(
            {"update_records": {rid: {BASE_FIELD_LIKE: r["like"],
                                      BASE_FIELD_CLICK: r["click"]}}},
            ensure_ascii=False,
        )
        _lark_base(["base", "+record-batch-update", "--base-token", BASE_TOKEN,
                    "--table-id", TABLE_ID, "--json", payload, "--as", "user"])
        print("[sync] base updated %s like=%d click=%d" % (rid, r["like"], r["click"]))

    threading.Thread(target=_job, daemon=True).start()


# --- Card rendering (S2 template + live counters) ----------------------------

def _locate_source_blocks(card):
    """Return [(block_dict, source_id)] for the interactive_container that owns a
    button whose behaviors.value.source_id is set. The button's tag is `button`,
    not `interactive_container`, so we track the nearest ancestor container."""
    found = []

    def walk(node, ancestor=None):
        if isinstance(node, dict):
            cur_anc = node if node.get("tag") == "interactive_container" else ancestor
            sid = None
            bs = node.get("behaviors") if isinstance(node.get("behaviors"), list) else []
            for b in bs:
                if isinstance(b, dict) and b.get("type") == "callback":
                    sid = (b.get("value") or {}).get("source_id")
                    if sid:
                        break
            if sid and cur_anc is not None:
                found.append((cur_anc, sid))
            for v in node.values():
                walk(v, cur_anc)
        elif isinstance(node, list):
            for it in node:
                walk(it, ancestor)

    walk(card)
    return found


def _replace_in_block(block, new_count):
    elts = block.get("elements")
    if not isinstance(elts, list):
        return
    for el in elts:
        if (isinstance(el, dict) and el.get("tag") == "markdown"
                and "👁" in el.get("content", "")):
            el["content"] = re.sub(r"👁 \d+ · 👍 \d+", new_count, el["content"])
            return


def _replace_substring(card, old, new):
    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "content" and isinstance(v, str) and old in v:
                    node[k] = v.replace(old, new)
                else:
                    walk(v)
        elif isinstance(node, list):
            for it in node:
                walk(it)

    walk(card)


def build_card():
    """Render the full Card 2.0 JSON from the confirmed S2 template, with live
    like/click counters injected per data source."""
    rows = {r["id"]: r for r in get_rows()}
    votes = get_votes()
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        card = json.load(f)
    for block, sid in _locate_source_blocks(card):
        r = rows.get(sid)
        if not r:
            continue
        _replace_in_block(block, "👁 %d · 👍 %d" % (r["click"], r["like"]))
    fb_total = sum(votes.get(k, 0) for k, _ in FEEDBACK_VOTES)
    _replace_substring(card, "共 0 人反馈", "共 %d 人反馈" % fb_total)
    return card


def handle_callback(event):
    """Handle a card.action.trigger event -> HTTP response body."""
    action = (event or {}).get("action") or {}
    value = action.get("value") or {}
    kind = value.get("action")
    source_id = value.get("source_id")
    key = value.get("key")

    if kind == "like" and source_id:
        like_source(source_id)
        sync_to_base(source_id)
        return {
            "toast": {"type": "info", "content": "感谢点赞 👍"},
            "card": {"type": "update",
                     "data": json.dumps(build_card(), ensure_ascii=False)},
        }
    if kind == "open" and source_id:
        click_source(source_id)
        sync_to_base(source_id)
        return {
            "toast": {"type": "info", "content": "已记录点击"},
            "actions": [{"type": "open_url", "default_url": real_url(source_id)}],
        }
    if kind == "vote" and key in VOTE_KEYS:
        bump_vote(key)
        return {
            "toast": {"type": "info", "content": "已记录你的选择"},
            "card": {"type": "update",
                     "data": json.dumps(build_card(), ensure_ascii=False)},
        }
    if kind == "drill":
        enqueue(value.get("label", "追一下：热点主线"))
        n = len(get_queue())
        return {
            "toast": {"type": "info",
                      "content": "已加入研究队列（第 %d 条），下次追踪优先展开" % n},
            "card": {"type": "update",
                     "data": json.dumps(build_card(), ensure_ascii=False)},
        }
    return {"toast": {"type": "info", "content": "未识别的操作"}}


def _extract_event(payload):
    """Normalize a Feishu push into an event dict (or a verify marker).

    Feishu ships card callbacks in two shapes:
      * legacy:  {"type":"event_callback","event_type":"card.action.trigger","event":{...}}
      * current: {"schema":"2.0","header":{"event_type":"card.action.trigger",...},"event":{...}}
    Plus the one-off `url_verification` challenge during subscription setup.
    """
    if payload.get("type") == "url_verification":
        return {"__verify__": payload.get("challenge", "")}
    if (payload.get("schema") == "2.0"
            and payload.get("header", {}).get("event_type") == "card.action.trigger"):
        return payload.get("event", {})
    if (payload.get("type") == "event_callback"
            and payload.get("event_type") == "card.action.trigger"):
        return payload.get("event", {})
    ev = payload.get("event", {})
    if isinstance(ev, dict) and (ev.get("type") == "card.action.trigger"
                                 or payload.get("event_type") == "card.action.trigger"):
        return ev
    return {}


class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/stats":
            self._send({"sources": get_rows(), "votes": get_votes(),
                        "queue": get_queue(), "base_url": BASE_URL})
            return
        if parsed.path == "/queue":
            self._send({"queue": get_queue()})
            return
        if parsed.path.startswith("/r/"):
            sid = parsed.path[len("/r/"):]
            click_source(sid)
            sync_to_base(sid)
            self.send_response(302)
            self.send_header("Location", real_url(sid))
            self.end_headers()
            return
        self._send({"ok": True, "msg": "hotspot card counter"}, 200)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}
        event = _extract_event(payload)
        if isinstance(event, dict) and "__verify__" in event:
            self._send({"challenge": event["__verify__"]})
            return
        if event and (event.get("type") == "card.action.trigger"
                      or payload.get("event_type") == "card.action.trigger"):
            self._send(handle_callback(event))
            return
        self._send({"ok": True})

    def log_message(self, *a):
        pass


def serve(host, port):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print("serving on http://%s:%d  (BASE_URL=%s)" % (host, port, BASE_URL))
    print("  POST /feishu/callback   card actions (like/open/vote/drill)")
    print("  GET  /stats             like/click/vote/queue state")
    print("  GET  /r/<id>            fallback 302 redirect counter")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


def main():
    ap = argparse.ArgumentParser(description="Hotspot card interactive backend.")
    ap.add_argument("--seed", action="store_true", help="insert sources + vote keys")
    ap.add_argument("--build-card", action="store_true", help="render card JSON from DB")
    ap.add_argument("--out", help="output card JSON path (with --build-card)")
    ap.add_argument("--stats", action="store_true", help="print current state")
    ap.add_argument("--ensure-base", action="store_true",
                    help="create 点赞数/点击数 fields + build url→record map")
    ap.add_argument("--serve", action="store_true", help="run the HTTP server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    args = ap.parse_args()

    if args.seed:
        seed()
    if args.ensure_base:
        ensure_base_fields()
        m = ensure_url_map()
        print("url_map built:", len(m), "records")
    if args.build_card:
        card = build_card()
        out = args.out or "hotspot_card_interactive.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(card, f, ensure_ascii=False, indent=2)
        print("card written -> %s (%d bytes)" % (out, os.path.getsize(out)))
    if args.stats:
        print(json.dumps({"sources": get_rows(), "votes": get_votes(),
                          "queue": get_queue()}, ensure_ascii=False, indent=2))
    if args.serve:
        serve(args.host, args.port)


if __name__ == "__main__":
    main()
