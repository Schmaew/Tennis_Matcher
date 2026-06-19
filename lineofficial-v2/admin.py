"""
admin.py
================================================================
Tiny admin dashboard at /admin.

Auth: Bearer token. Send the header

    Authorization: Bearer <ADMIN_TOKEN>

The dashboard fetches /admin/players and renders a table.

If ADMIN_PATH_SECRET is set in .env, the URL becomes
/<secret>/admin instead of /admin (defense-in-depth — same trick
the senior's repo uses to hide the panel from random scanners).

🎓 CUSTOMIZE: add new admin pages by adding routes to this blueprint.
   The HTML at the bottom is intentionally one file with inline CSS;
   if it grows past ~200 lines, split into a templates/ folder.
================================================================
"""

import os
import hmac
from collections import Counter
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, request, jsonify, abort

from linebot.v3.messaging import MulticastRequest, TextMessage

import db

_ADMIN_PATH_SECRET = (os.environ.get("ADMIN_PATH_SECRET") or "").strip()
_BASE = f"/{_ADMIN_PATH_SECRET}/admin" if _ADMIN_PATH_SECRET else "/admin"

admin_bp = Blueprint("admin", __name__, url_prefix=_BASE)


def admin_base_path() -> str:
    """server.py logs this on startup so the operator knows the URL."""
    return _BASE


def _check_auth() -> bool:
    """Constant-time Bearer-token check (mirrors senior's admin-auth.js)."""
    expected = os.environ.get("ADMIN_TOKEN", "")
    header = request.headers.get("Authorization", "")
    if not expected or not header.startswith("Bearer "):
        return False
    token = header[len("Bearer "):]
    if len(token) != len(expected):
        return False
    return hmac.compare_digest(token, expected)


@admin_bp.route("", methods=["GET"])
def dashboard():
    # The HTML page itself is public — no secrets in markup.
    # The /players JSON endpoint is what's auth-protected.
    return _DASHBOARD_HTML.replace("__ADMIN_BASE__", _BASE), 200, {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-store, must-revalidate",
        "Pragma": "no-cache",
    }


@admin_bp.route("/players", methods=["GET"])
def players():
    if not _check_auth():
        abort(401)
    rows = db.get_all_players()
    return jsonify(rows)


@admin_bp.route("/matches", methods=["GET"])
def matches():
    if not _check_auth():
        abort(401)
    # Most recent 20 matches with player nicknames stitched in.
    res = db._sb.table("matches").select("*").order("suggested_at", desc=True).limit(20).execute()
    players_by_id = {p["line_user_id"]: p for p in db.get_all_players()}

    def nick(uid: str) -> str:
        return (players_by_id.get(uid) or {}).get("nickname") or uid[:8]

    enriched = [{
        "id": m["id"],
        "a_nick": nick(m["player_a_id"]),
        "b_nick": nick(m["player_b_id"]),
        "a_response": m["player_a_response"],
        "b_response": m["player_b_response"],
        "introduced": m["introduced"],
        "suggested_at": m["suggested_at"],
    } for m in (res.data or [])]
    return jsonify(enriched)


@admin_bp.route("/queue", methods=["GET"])
def queue():
    if not _check_auth():
        abort(401)
    try:
        rows = db.get_waiting_queue()
    except Exception as e:
        return jsonify({"error": f"queue table missing — run add_waiting_queue.sql ({e})"}), 200
    players_by_id = {p["line_user_id"]: p for p in db.get_all_players()}
    enriched = [{
        "line_user_id": r["line_user_id"],
        "nickname": (players_by_id.get(r["line_user_id"]) or {}).get("nickname") or "-",
        "area":     (players_by_id.get(r["line_user_id"]) or {}).get("area") or "-",
        "queued_at": r["queued_at"],
    } for r in rows]
    return jsonify(enriched)


@admin_bp.route("/skips", methods=["GET"])
def skips():
    if not _check_auth():
        abort(401)
    rows = db.get_all_skips()
    players_by_id = {p["line_user_id"]: p for p in db.get_all_players()}

    def nick(uid: str) -> str:
        return (players_by_id.get(uid) or {}).get("nickname") or uid[:8]

    enriched = [{
        "skipper_id":   r["skipper_id"],
        "skipped_id":   r["skipped_id"],
        "skipper_nick": nick(r["skipper_id"]),
        "skipped_nick": nick(r["skipped_id"]),
        "count":        r["count"],
        "updated_at":   r["updated_at"],
    } for r in rows]
    return jsonify(enriched)


@admin_bp.route("/analytics", methods=["GET"])
def analytics():
    if not _check_auth():
        abort(401)
    players_all = db.get_all_players()

    # Onboarding funnel: count by status, and within onboarding, by step.
    funnel = {
        "registered": len(players_all),
        "onboarding": 0,
        "active": 0,
        "paused": 0,
        "by_step": {str(i): 0 for i in range(1, 6)},
    }
    for p in players_all:
        funnel[p["status"]] = funnel.get(p["status"], 0) + 1
        if p["status"] == "onboarding":
            step = str(p.get("onboarding_step") or 0)
            if step in funnel["by_step"]:
                funnel["by_step"][step] += 1

    # Signups per day for the last 14 days, in chronological order.
    today = datetime.now(timezone.utc).date()
    bucket = Counter()
    for p in players_all:
        try:
            d = datetime.fromisoformat(p["registered_at"].replace("Z", "+00:00")).date()
        except Exception:
            continue
        bucket[d] += 1
    signups = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        signups.append({"date": d.isoformat(), "count": bucket.get(d, 0)})

    return jsonify({"funnel": funnel, "signups": signups})


@admin_bp.route("/player/<line_user_id>", methods=["GET"])
def player_detail(line_user_id):
    if not _check_auth():
        abort(401)
    player = db.get_player(line_user_id)
    if not player:
        abort(404)
    matches = db.get_matches_for(line_user_id)
    skips_made, skips_received = db.get_skips_involving(line_user_id)
    players_by_id = {p["line_user_id"]: p for p in db.get_all_players()}

    def nick(uid: str) -> str:
        return (players_by_id.get(uid) or {}).get("nickname") or uid[:8]

    return jsonify({
        "player": player,
        "matches": [{
            "id": m["id"],
            "opponent": nick(
                m["player_b_id"] if m["player_a_id"] == line_user_id else m["player_a_id"]
            ),
            "your_response": (
                m["player_a_response"] if m["player_a_id"] == line_user_id
                else m["player_b_response"]
            ),
            "their_response": (
                m["player_b_response"] if m["player_a_id"] == line_user_id
                else m["player_a_response"]
            ),
            "introduced": m["introduced"],
            "suggested_at": m["suggested_at"],
        } for m in matches],
        "skips_made":     [{"who": nick(s["skipped_id"]), "count": s["count"]} for s in skips_made],
        "skips_received": [{"who": nick(s["skipper_id"]), "count": s["count"]} for s in skips_received],
    })


@admin_bp.route("/broadcast", methods=["POST"])
def broadcast():
    if not _check_auth():
        abort(401)
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"error": "empty text"}), 400
    if len(text) > 1000:
        return jsonify({"error": "text too long (>1000 chars)"}), 400

    line_api = current_app.config.get("LINE_API")
    if not line_api:
        return jsonify({"error": "LINE_API not configured"}), 500

    user_ids = [
        p["line_user_id"] for p in db.get_all_players()
        if p["status"] == "active"
    ]
    if not user_ids:
        return jsonify({"sent_to": 0, "batches": 0})

    # LINE multicast caps at 500 recipients per call.
    batches = 0
    failures = []
    for i in range(0, len(user_ids), 500):
        chunk = user_ids[i:i + 500]
        try:
            line_api.multicast(MulticastRequest(to=chunk, messages=[TextMessage(text=text)]))
            batches += 1
        except Exception as e:
            failures.append(str(e)[:200])
    return jsonify({"sent_to": len(user_ids), "batches": batches, "failures": failures})


@admin_bp.route("/stats", methods=["GET"])
def stats():
    if not _check_auth():
        abort(401)
    players_all = db.get_all_players()
    by_status: dict[str, int] = {}
    for p in players_all:
        by_status[p["status"]] = by_status.get(p["status"], 0) + 1

    matches_res = db._sb.table("matches").select("introduced", count="exact").execute()
    total_matches = matches_res.count or 0
    introduced_res = (
        db._sb.table("matches").select("introduced", count="exact").eq("introduced", True).execute()
    )
    introduced_count = introduced_res.count or 0

    try:
        queue_len = len(db.get_waiting_queue())
    except Exception:
        queue_len = None  # table not migrated yet

    return jsonify({
        "players_total":  len(players_all),
        "players_active": by_status.get("active", 0),
        "players_onboarding": by_status.get("onboarding", 0),
        "players_paused": by_status.get("paused", 0),
        "matches_total": total_matches,
        "matches_introduced": introduced_count,
        "queue_length": queue_len,
    })


# Keep the HTML simple enough to read in one screen.
_DASHBOARD_HTML = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>Tennis Matcher — Admin</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }
  h1 { color: #2ECC71; margin-bottom: .25rem; }
  h2 { color: #333; margin-top: 2.5rem; border-bottom: 1px solid #eee; padding-bottom: .25rem; }
  input, button { padding: .5rem; font-size: 1rem; }
  button { background: #2ECC71; color: white; border: 0; border-radius: 6px; cursor: pointer; }
  button:hover { background: #27AE60; }
  table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: .92rem; }
  th, td { padding: .5rem; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f7f7f7; }
  .pill { display: inline-block; padding: .15rem .5rem; border-radius: 999px; font-size: .82rem; font-weight: 500; }
  .pill.active     { background: #d4edda; color: #155724; }
  .pill.onboarding { background: #fff3cd; color: #856404; }
  .pill.paused     { background: #e2e3e5; color: #383d41; }
  .pill.accepted   { background: #d4edda; color: #155724; }
  .pill.declined   { background: #f8d7da; color: #721c24; }
  .pill.pending    { background: #fff3cd; color: #856404; }
  .pill.introduced { background: #cce5ff; color: #004085; }

  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: .75rem; margin-top: 1.5rem; }
  .stat { background: #f7f9fc; border: 1px solid #e1e5ea; border-radius: 8px; padding: 1rem; text-align: center; }
  .stat .n     { font-size: 1.75rem; font-weight: 700; color: #2ECC71; line-height: 1.1; }
  .stat .label { font-size: .8rem; color: #555; text-transform: uppercase; letter-spacing: .03em; margin-top: .25rem; }
  .err { color: #b00; font-style: italic; }
  .muted { color: #888; font-size: .85rem; }

  /* Charts (CSS-only bars, no library) */
  .chart .row { display: flex; align-items: center; gap: .5rem; margin: .2rem 0; font-size: .88rem; }
  .chart .row .label { width: 110px; flex-shrink: 0; color: #444; }
  .chart .row .bar   { background: #2ECC71; color: white; padding: .15rem .5rem; border-radius: 4px; min-width: 1.5rem; text-align: right; }
  .chart .row .bar.empty { background: #eee; color: #aaa; }

  /* Player drill-down modal */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: none; z-index: 10; }
  .modal-backdrop.open { display: flex; align-items: center; justify-content: center; }
  .modal { background: white; max-width: 760px; width: 92%; max-height: 90vh; overflow-y: auto; border-radius: 10px; padding: 1.5rem; position: relative; }
  .modal .close { position: absolute; top: .5rem; right: .75rem; background: transparent; color: #555; font-size: 1.5rem; border: 0; cursor: pointer; }
  tr.clickable { cursor: pointer; }
  tr.clickable:hover { background: #f3f8f3; }

  /* Broadcast */
  textarea { width: 100%; padding: .5rem; font-size: .95rem; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
  .broadcast-result { margin-top: .5rem; font-size: .9rem; }
  .danger { background: #E74C3C; }
  .danger:hover { background: #C0392B; }
</style>
</head>
<body>
<h1>🎾 Tennis Matcher — Admin</h1>
<p class="muted">Paste <code>ADMIN_TOKEN</code> and load. <span id="loaded" class="muted"></span></p>
<input id="token" type="password" placeholder="ADMIN_TOKEN" style="width: 60%">
<button onclick="load()">Load</button>

<div id="stats"   class="stats"></div>

<h2>Onboarding funnel</h2>
<div id="funnel" class="chart"></div>

<h2>Signups — last 14 days</h2>
<div id="signups" class="chart"></div>

<h2>Players <span class="muted">(click a row for details)</span></h2>
<div id="players"></div>

<h2>Recent matches</h2>     <div id="matches"></div>
<h2>Waiting queue (FIFO)</h2> <div id="queue"></div>
<h2>Skips <span class="muted">(who keeps getting skipped)</span></h2>
<div id="skips"></div>

<h2>Broadcast to active players</h2>
<p class="muted">Pushes a single message to <b>every active player</b>. Be careful — there is no undo.</p>
<textarea id="bcast-text" rows="3" placeholder="ข้อความที่จะส่ง..."></textarea>
<button class="danger" onclick="broadcast()">Send to all active players</button>
<div id="bcast-result" class="broadcast-result"></div>

<!-- Drill-down modal -->
<div id="modal" class="modal-backdrop" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <button class="close" onclick="closeModal()">&times;</button>
    <div id="modal-body"></div>
  </div>
</div>

<script>
const base = '__ADMIN_BASE__';

function pill(cls, text) {
  return '<span class="pill ' + cls + '">' + text + '</span>';
}
function statTile(n, label) {
  const v = (n === null || n === undefined) ? '—' : n;
  return '<div class="stat"><div class="n">' + v + '</div><div class="label">' + label + '</div></div>';
}
async function getJSON(path, token) {
  const res = await fetch(base + path, { headers: { 'Authorization': 'Bearer ' + token } });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}

async function loadOne(path, token, divId, render) {
  try {
    const data = await getJSON(path, token);
    render(data);
  } catch (e) {
    document.getElementById(divId).innerHTML =
      '<p class="err">' + path + ' failed: ' + e.message + '</p>';
  }
}

async function load() {
  const token = document.getElementById('token').value;
  document.getElementById('loaded').textContent = 'loading…';
  await Promise.all([
    loadOne('/stats',     token, 'stats',    renderStats),
    loadOne('/analytics', token, 'funnel',   renderAnalytics),
    loadOne('/players',   token, 'players',  renderPlayers),
    loadOne('/matches',   token, 'matches',  renderMatches),
    loadOne('/queue',     token, 'queue',    renderQueue),
    loadOne('/skips',     token, 'skips',    renderSkips),
  ]);
  document.getElementById('loaded').textContent =
    'loaded ' + new Date().toLocaleTimeString();
}

function renderAnalytics(a) {
  // Funnel (in #funnel)
  const totals = [
    ['Registered', a.funnel.registered],
    ['Onboarding', a.funnel.onboarding],
    ['Active',     a.funnel.active],
    ['Paused',     a.funnel.paused],
  ];
  const max1 = Math.max(1, ...totals.map(x => x[1]));
  let html = '';
  for (const [label, n] of totals) html += bar(label, n, max1);
  html += '<div class="muted" style="margin-top:.75rem;">Onboarding breakdown by step</div>';
  const steps = a.funnel.by_step;
  const max2 = Math.max(1, ...Object.values(steps));
  for (const k of Object.keys(steps).sort()) html += bar('Step ' + k, steps[k], max2);
  document.getElementById('funnel').innerHTML = html;

  // Signups (in #signups)
  const max3 = Math.max(1, ...a.signups.map(x => x.count));
  let html2 = '';
  for (const d of a.signups) html2 += bar(d.date.slice(5), d.count, max3);
  document.getElementById('signups').innerHTML = html2;
}

function bar(label, n, max) {
  const pct = Math.round((n / max) * 100);
  const cls = n === 0 ? 'bar empty' : 'bar';
  return '<div class="row"><div class="label">' + label + '</div>'
       + '<div class="' + cls + '" style="width: ' + pct + '%">' + n + '</div></div>';
}

function renderSkips(rows) {
  if (!rows.length) { document.getElementById('skips').innerHTML = '<p class="muted">No skips recorded yet.</p>'; return; }
  const html = ['<table><thead><tr>',
    '<th>Skipper</th><th>Skipped</th><th>Count</th><th>Last skip</th>',
    '</tr></thead><tbody>'];
  for (const r of rows) {
    html.push('<tr>',
      '<td>', r.skipper_nick, '</td>',
      '<td>', r.skipped_nick, '</td>',
      '<td><b>', r.count, '</b></td>',
      '<td>', new Date(r.updated_at).toLocaleString(), '</td>',
      '</tr>');
  }
  html.push('</tbody></table>');
  document.getElementById('skips').innerHTML = html.join('');
}

async function openPlayer(uid) {
  const token = document.getElementById('token').value;
  const body = document.getElementById('modal-body');
  body.innerHTML = '<p class="muted">Loading…</p>';
  document.getElementById('modal').classList.add('open');
  try {
    const d = await getJSON('/player/' + encodeURIComponent(uid), token);
    const p = d.player;
    const lid = p.line_basic_id ? ('@' + p.line_basic_id) : '-';
    const hdr = '<h2 style="margin-top:0">' + (p.nickname || '-') + ' ' + pill(p.status, p.status) + '</h2>'
              + '<p class="muted">Skill: ' + (p.skill_level || '-')
              + ' &middot; Area: ' + (p.area || '-')
              + ' &middot; LINE: ' + lid + '</p>';

    let mh = '<h3>Matches (' + d.matches.length + ')</h3>';
    if (!d.matches.length) mh += '<p class="muted">None yet.</p>';
    else {
      mh += '<table><thead><tr><th>#</th><th>Opponent</th><th>You</th><th>Them</th><th>Intro?</th><th>When</th></tr></thead><tbody>';
      for (const m of d.matches) {
        mh += '<tr>'
            + '<td>' + m.id + '</td>'
            + '<td>' + m.opponent + '</td>'
            + '<td>' + pill(m.your_response, m.your_response) + '</td>'
            + '<td>' + pill(m.their_response, m.their_response) + '</td>'
            + '<td>' + (m.introduced ? '✓' : '') + '</td>'
            + '<td>' + new Date(m.suggested_at).toLocaleString() + '</td>'
            + '</tr>';
      }
      mh += '</tbody></table>';
    }

    function skipTable(title, rows) {
      let h = '<h3>' + title + ' (' + rows.length + ')</h3>';
      if (!rows.length) return h + '<p class="muted">None.</p>';
      h += '<table><thead><tr><th>Who</th><th>Count</th></tr></thead><tbody>';
      for (const s of rows) h += '<tr><td>' + s.who + '</td><td><b>' + s.count + '</b></td></tr>';
      return h + '</tbody></table>';
    }

    body.innerHTML = hdr + mh
      + skipTable('Players they skipped', d.skips_made)
      + skipTable('Players who skipped them', d.skips_received);
  } catch (e) {
    body.innerHTML = '<p class="err">Load failed: ' + e.message + '</p>';
  }
}
function closeModal() { document.getElementById('modal').classList.remove('open'); }

async function broadcast() {
  const token = document.getElementById('token').value;
  const text  = document.getElementById('bcast-text').value.trim();
  if (!text) { alert('Type a message first.'); return; }
  if (!confirm('Send this to EVERY active player? This cannot be undone.\\n\\n' + text)) return;
  const res = await fetch(base + '/broadcast', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  const out = await res.json();
  const el = document.getElementById('bcast-result');
  if (!res.ok) {
    el.innerHTML = '<span class="err">Failed: ' + (out.error || res.status) + '</span>';
  } else {
    el.innerHTML = '<span style="color:#155724">Sent to ' + out.sent_to + ' user(s) in '
                 + out.batches + ' batch(es)' + (out.failures && out.failures.length ? ' — failures: ' + out.failures.join(' | ') : '') + '</span>';
    document.getElementById('bcast-text').value = '';
  }
}

function renderStats(s) {
  document.getElementById('stats').innerHTML = [
    statTile(s.players_total,       'Players'),
    statTile(s.players_active,      'Active'),
    statTile(s.players_onboarding,  'Onboarding'),
    statTile(s.players_paused,      'Paused'),
    statTile(s.matches_total,       'Total matches'),
    statTile(s.matches_introduced,  'Introduced'),
    statTile(s.queue_length,        'In queue'),
  ].join('');
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderPlayers(rows) {
  if (!rows.length) { document.getElementById('players').innerHTML = '<p class="muted">No players.</p>'; return; }
  const html = ['<table><thead><tr>',
    '<th>Nickname</th><th>Status</th><th>Skill</th><th>Area</th><th>LINE ID</th><th>Registered</th>',
    '</tr></thead><tbody>'];
  for (const r of rows) {
    html.push('<tr class="clickable" data-uid="', esc(r.line_user_id), '">',
      '<td>', esc(r.nickname || '-'), '</td>',
      '<td>', pill(r.status, r.status), '</td>',
      '<td>', esc(r.skill_level || '-'), '</td>',
      '<td>', esc(r.area || '-'), '</td>',
      '<td>', r.line_basic_id ? ('@' + esc(r.line_basic_id)) : '<span class="muted">-</span>', '</td>',
      '<td>', new Date(r.registered_at).toLocaleString(), '</td>',
      '</tr>');
  }
  html.push('</tbody></table>');
  const root = document.getElementById('players');
  root.innerHTML = html.join('');
  // Delegated row click → openPlayer
  root.onclick = (e) => {
    const tr = e.target.closest('tr.clickable');
    if (tr && tr.dataset.uid) openPlayer(tr.dataset.uid);
  };
}

function renderMatches(rows) {
  if (!rows.length) { document.getElementById('matches').innerHTML = '<p class="muted">No matches yet.</p>'; return; }
  const html = ['<table><thead><tr>',
    '<th>#</th><th>Player A</th><th>A resp.</th><th>Player B</th><th>B resp.</th><th>Status</th><th>When</th>',
    '</tr></thead><tbody>'];
  for (const r of rows) {
    const status = r.introduced ? pill('introduced', 'introduced') :
                   (r.a_response === 'declined' || r.b_response === 'declined') ? pill('declined', 'dead') :
                   pill('pending', 'live');
    html.push('<tr>',
      '<td>', r.id, '</td>',
      '<td>', r.a_nick, '</td>',
      '<td>', pill(r.a_response, r.a_response), '</td>',
      '<td>', r.b_nick, '</td>',
      '<td>', pill(r.b_response, r.b_response), '</td>',
      '<td>', status, '</td>',
      '<td>', new Date(r.suggested_at).toLocaleString(), '</td>',
      '</tr>');
  }
  html.push('</tbody></table>');
  document.getElementById('matches').innerHTML = html.join('');
}

function renderQueue(rows) {
  if (rows && rows.error) {
    document.getElementById('queue').innerHTML = '<p class="err">' + rows.error + '</p>';
    return;
  }
  if (!rows.length) { document.getElementById('queue').innerHTML = '<p class="muted">Queue is empty.</p>'; return; }
  const html = ['<table><thead><tr>',
    '<th>#</th><th>Nickname</th><th>Area</th><th>Queued at</th>',
    '</tr></thead><tbody>'];
  rows.forEach((r, i) => {
    html.push('<tr>',
      '<td>', i + 1, '</td>',
      '<td>', r.nickname, '</td>',
      '<td>', r.area, '</td>',
      '<td>', new Date(r.queued_at).toLocaleString(), '</td>',
      '</tr>');
  });
  html.push('</tbody></table>');
  document.getElementById('queue').innerHTML = html.join('');
}
</script>
</body>
</html>
"""
