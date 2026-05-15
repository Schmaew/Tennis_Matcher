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
from flask import Blueprint, request, jsonify, abort

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
    }


@admin_bp.route("/players", methods=["GET"])
def players():
    if not _check_auth():
        abort(401)
    rows = db.get_all_players()
    return jsonify(rows)


# Keep the HTML simple enough to read in one screen.
_DASHBOARD_HTML = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>Tennis Matcher — Admin</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
  h1 { color: #2ECC71; }
  input, button { padding: .5rem; font-size: 1rem; }
  table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
  th, td { padding: .5rem; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f7f7f7; }
  .pill { display: inline-block; padding: .15rem .5rem; border-radius: 999px; font-size: .85rem; }
  .pill.active { background: #d4edda; color: #155724; }
  .pill.onboarding { background: #fff3cd; color: #856404; }
  .pill.paused { background: #e2e3e5; color: #383d41; }
</style>
</head>
<body>
<h1>🎾 Tennis Matcher — Admin</h1>
<p>Paste your <code>ADMIN_TOKEN</code> to load the player list.</p>
<input id="token" type="password" placeholder="ADMIN_TOKEN" style="width: 60%">
<button onclick="load()">Load players</button>
<div id="out"></div>
<script>
async function load() {
  const token = document.getElementById('token').value;
  const res = await fetch('__ADMIN_BASE__/players', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (!res.ok) {
    document.getElementById('out').textContent = 'Auth failed (HTTP ' + res.status + ')';
    return;
  }
  const rows = await res.json();
  const html = ['<table><thead><tr>',
    '<th>Nickname</th><th>Status</th><th>Skill</th><th>Area</th><th>Registered</th>',
    '</tr></thead><tbody>'];
  for (const r of rows) {
    html.push('<tr>',
      '<td>', r.nickname || '-', '</td>',
      '<td><span class="pill ', r.status, '">', r.status, '</span></td>',
      '<td>', r.skill_level || '-', '</td>',
      '<td>', r.area || '-', '</td>',
      '<td>', new Date(r.registered_at).toLocaleString(), '</td>',
      '</tr>');
  }
  html.push('</tbody></table>');
  document.getElementById('out').innerHTML = html.join('');
}
</script>
</body>
</html>
"""
