#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

DEFAULT_REQ_DIRS = ["reqs/mon"]
DEFAULT_TEST_DIRS = ["reqs/tst"]
DEFAULT_TEST_SCAN_DIRS: list[str] = []
SCAN_SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
}
DIRECTIVE_RE = re.compile(
    r"^\s*(?:#|//|--|;|/\*+|\*+)?\s*(HODOR-[A-Z-]+)\s*:\s*(.*)$"
)
SKIP_NAMES = {
    ".doorstop.yml",
    "doorstop.yml",
    ".doorstop.skip",
    ".doorstop.skip-all",
}

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__TITLE__</title>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #f6f1e8;
      --bg-2: #f0e7da;
      --panel: #ffffff;
      --ink: #1f1a17;
      --muted: #6b5f55;
      --accent: #2d6f6b;
      --accent-2: #b25c34;
      --danger: #b3402a;
      --ok: #2e6b3d;
      --warn: #8a6d1f;
      --border: #e2d6c7;
      --shadow: 0 10px 30px rgba(35, 23, 15, 0.12);
      --radius: 14px;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "IBM Plex Sans", "Avenir Next", "Gill Sans", sans-serif;
      color: var(--ink);
      background: radial-gradient(1200px 600px at 10% 0%, #ffffff 0%, var(--bg) 40%, var(--bg-2) 100%);
    }

    .wrap {
      max-width: 1200px;
      margin: 0 auto;
      padding: 36px 20px 64px;
      position: relative;
    }

    .hero {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 28px 32px;
      box-shadow: var(--shadow);
      overflow: hidden;
      position: relative;
      animation: fadeUp 0.6s ease-out;
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(120deg, rgba(45,111,107,0.08), transparent 40%),
                  linear-gradient(-140deg, rgba(178,92,52,0.10), transparent 45%);
      pointer-events: none;
    }

    h1 {
      margin: 0 0 8px;
      font-family: "Fraunces", "Iowan Old Style", serif;
      font-size: clamp(28px, 4vw, 42px);
      letter-spacing: 0.2px;
    }

    .subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }

    .meta {
      margin-top: 14px;
      display: flex;
      gap: 18px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 13px;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin: 24px 0 20px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 18px;
      box-shadow: 0 6px 20px rgba(35, 23, 15, 0.08);
      animation: fadeUp 0.6s ease-out;
    }

    .card h3 {
      margin: 0 0 6px;
      font-size: 13px;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .card .value {
      font-size: 26px;
      font-weight: 600;
    }

    .card .value small {
      font-size: 13px;
      color: var(--muted);
    }

    .toolbar {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
      padding: 14px 16px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      margin-bottom: 18px;
    }

    .toolbar input[type="search"] {
      flex: 1 1 240px;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      font-size: 14px;
      background: #fbf8f3;
    }

    .toolbar select, .toolbar button {
      padding: 9px 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #fbf8f3;
      font-size: 14px;
    }

    .toggle {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--muted);
    }

    .section {
      margin-top: 26px;
    }

    .section h2 {
      font-family: "Fraunces", "Iowan Old Style", serif;
      font-size: 22px;
      margin: 0 0 12px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 6px 20px rgba(35, 23, 15, 0.08);
    }

    thead {
      background: #f5eee4;
    }

    th, td {
      padding: 12px 14px;
      text-align: left;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
      font-size: 13px;
    }

    th {
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }

    tbody tr:nth-child(odd) {
      background: #fcf9f4;
    }

    tbody tr:hover {
      background: #f1e8db;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid transparent;
    }

    .badge.ok {
      background: rgba(46, 107, 61, 0.12);
      color: var(--ok);
      border-color: rgba(46, 107, 61, 0.2);
    }

    .badge.warn {
      background: rgba(178, 92, 52, 0.12);
      color: var(--accent-2);
      border-color: rgba(178, 92, 52, 0.2);
    }

    .chip {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 8px;
      background: rgba(45,111,107,0.12);
      color: var(--accent);
      border: 1px solid rgba(45,111,107,0.2);
      font-size: 12px;
      margin-right: 6px;
      margin-bottom: 4px;
      font-family: "JetBrains Mono", "SFMono-Regular", Menlo, monospace;
    }

    .refs {
      font-family: "JetBrains Mono", "SFMono-Regular", Menlo, monospace;
      font-size: 12px;
      color: var(--muted);
      line-height: 1.4;
    }

    .muted { color: var(--muted); }

    .detail {
      margin-top: 18px;
      padding: 16px 18px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 6px 20px rgba(35, 23, 15, 0.08);
    }

    .detail pre {
      font-family: "JetBrains Mono", "SFMono-Regular", Menlo, monospace;
      background: #f9f4ec;
      padding: 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      white-space: pre-wrap;
      font-size: 12px;
      line-height: 1.5;
    }

    .matrix {
      margin-top: 16px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: var(--panel);
      overflow: auto;
      max-height: 420px;
    }

    .matrix table {
      border: none;
      box-shadow: none;
      min-width: 600px;
    }

    .matrix th, .matrix td {
      text-align: center;
      padding: 8px 10px;
    }

    .matrix th {
      position: sticky;
      top: 0;
      background: #f5eee4;
      z-index: 2;
    }

    .matrix .row-head {
      position: sticky;
      left: 0;
      background: #f5eee4;
      z-index: 1;
      text-align: left;
      font-family: "JetBrains Mono", "SFMono-Regular", Menlo, monospace;
    }

    .dot {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #d7c8b5;
    }

    .dot.on {
      background: var(--accent);
    }

    .footer {
      margin-top: 32px;
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 720px) {
      .hero { padding: 20px; }
      .toolbar { flex-direction: column; align-items: stretch; }
      th:nth-child(3), td:nth-child(3), th:nth-child(4), td:nth-child(4) { display: none; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>__TITLE__</h1>
      <p class="subtitle">__SUBTITLE__</p>
      <div class="meta">
        <div><strong>Source</strong>: __SOURCE_ROOT__</div>
        <div><strong>Generated</strong>: __GENERATED_AT__</div>
      </div>
    </section>

    <section class="cards" id="summary-cards"></section>

    <section class="toolbar">
      <input id="search" type="search" placeholder="Search by ID, text, or reference" />
      <select id="status-filter">
        <option value="all">All status</option>
        <option value="linked">Linked</option>
        <option value="unlinked">Unlinked</option>
      </select>
      <label class="toggle"><input id="show-matrix" type="checkbox" /> Show matrix</label>
      <label class="toggle"><input id="show-tests" type="checkbox" checked /> Show tests table</label>
      <button id="download-json">Download JSON</button>
      <button id="download-links">Download Links CSV</button>
    </section>

    <section class="section">
      <h2>Requirements Coverage</h2>
      <div id="req-table"></div>
      <div class="detail" id="req-detail"></div>
    </section>

    <section class="section" id="tests-section">
      <h2>Test Coverage</h2>
      <div id="test-table"></div>
    </section>

    <section class="section" id="matrix-section" style="display:none;">
      <h2>Traceability Matrix</h2>
      <div class="matrix" id="matrix"></div>
    </section>

    <div class="footer">Audit view generated from requirement items and in-test HODOR annotations.</div>
  </div>

  <script id="data" type="application/json">__DATA_JSON__</script>
  <script>
    const data = JSON.parse(document.getElementById('data').textContent);
    const searchInput = document.getElementById('search');
    const statusFilter = document.getElementById('status-filter');
    const showMatrix = document.getElementById('show-matrix');
    const showTests = document.getElementById('show-tests');
    const testsSection = document.getElementById('tests-section');
    const matrixSection = document.getElementById('matrix-section');

    const summary = data.summary;
    const summaryCards = [
      { label: 'Requirements', value: summary.requirements_total },
      { label: 'Linked Requirements', value: summary.requirements_linked },
      { label: 'Unlinked Requirements', value: summary.requirements_unlinked },
      { label: 'Tests', value: summary.tests_total },
      { label: 'Coverage', value: summary.coverage_pct + '%', sub: 'requirements linked' },
      { label: 'Total Links', value: summary.links_total },
    ];

    function renderCards() {
      const el = document.getElementById('summary-cards');
      el.innerHTML = summaryCards.map(card => `
        <div class="card">
          <h3>${card.label}</h3>
          <div class="value">${card.value}${card.sub ? ` <small>${card.sub}</small>` : ''}</div>
        </div>
      `).join('');
    }

    function filterItems(items) {
      const term = searchInput.value.trim().toLowerCase();
      const status = statusFilter.value;
      return items.filter(item => {
        const matchesStatus = status === 'all' || item.status === status;
        const related = item.tests || item.reqs || [];
        const hay = [
          item.id,
          item.text,
          (item.refs || []).join(' '),
          related.join(' '),
          (item.links || []).join(' '),
        ].join(' ').toLowerCase();
        const matchesTerm = !term || hay.includes(term);
        return matchesStatus && matchesTerm;
      });
    }

    function renderReqTable() {
      const rows = filterItems(data.requirements);
      const html = [
        '<table>',
        '<thead><tr><th>ID</th><th>Requirement</th><th>Tests</th><th>Status</th></tr></thead>',
        '<tbody>',
        ...rows.map(req => {
          const tests = req.tests.length ? req.tests.map(t => `<span class="chip">${t}</span>`).join('') : '<span class="muted">None</span>';
          const status = req.status === 'linked' ? '<span class="badge ok">Linked</span>' : '<span class="badge warn">Unlinked</span>';
          return `<tr data-req="${req.id}"><td><strong>${req.id}</strong></td><td>${req.text.split('\n')[0]}</td><td>${tests}</td><td>${status}</td></tr>`;
        }),
        '</tbody></table>'
      ].join('');
      document.getElementById('req-table').innerHTML = html;

      const detail = document.getElementById('req-detail');
      const reqMap = Object.fromEntries(data.requirements.map(r => [r.id, r]));
      const testMap = Object.fromEntries(data.tests.map(t => [t.id, t]));
      document.querySelectorAll('#req-table tbody tr').forEach(row => {
        row.addEventListener('click', () => {
          const id = row.getAttribute('data-req');
          const req = reqMap[id];
          const linked = req.tests.length
            ? req.tests.map(t => {
                const refs = (testMap[t].refs || []).map(r => `<div class="refs">${r}</div>`).join('') || '<div class="refs muted">No references</div>';
                return `<div style="margin-bottom:8px;"><span class="chip">${t}</span>${refs}</div>`;
              }).join('')
            : '<span class="muted">None</span>';
          detail.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
              <div><strong>${req.id}</strong></div>
              <div>${req.status === 'linked' ? '<span class="badge ok">Linked</span>' : '<span class="badge warn">Unlinked</span>'}</div>
            </div>
            <p class="muted">${req.path}</p>
            <pre>${req.text}</pre>
            <div><strong>Linked tests</strong>:</div>
            <div>${linked}</div>
          `;
        });
      });

      if (rows.length) {
        const first = document.querySelector('#req-table tbody tr');
        if (first) { first.click(); }
      } else {
        detail.innerHTML = '<div class="muted">No matching requirements.</div>';
      }
    }

    function renderTestTable() {
      const rows = filterItems(data.tests);
      const html = [
        '<table>',
        '<thead><tr><th>ID</th><th>Test</th><th>Linked Requirements</th><th>References</th><th>Status</th></tr></thead>',
        '<tbody>',
        ...rows.map(test => {
          const reqs = test.reqs.length ? test.reqs.map(r => `<span class="chip">${r}</span>`).join('') : '<span class="muted">None</span>';
          const refs = (test.refs || []).length ? test.refs.map(r => `<div class="refs">${r}</div>`).join('') : '<span class="muted">None</span>';
          const status = test.status === 'linked' ? '<span class="badge ok">Linked</span>' : '<span class="badge warn">Unlinked</span>';
          return `<tr><td><strong>${test.id}</strong></td><td>${test.text.split('\n')[0]}</td><td>${reqs}</td><td>${refs}</td><td>${status}</td></tr>`;
        }),
        '</tbody></table>'
      ].join('');
      document.getElementById('test-table').innerHTML = html;
    }

    function renderMatrix() {
      const reqs = data.requirements;
      const tests = data.tests;
      const linkSet = new Set(data.links.map(l => `${l.req}::${l.test}`));
      const head = ['<th></th>', ...tests.map(t => `<th>${t.id}</th>`)].join('');
      const body = reqs.map(r => {
        const cells = tests.map(t => {
          const on = linkSet.has(`${r.id}::${t.id}`);
          return `<td><span class="dot ${on ? 'on' : ''}"></span></td>`;
        }).join('');
        return `<tr><th class="row-head">${r.id}</th>${cells}</tr>`;
      }).join('');
      document.getElementById('matrix').innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
    }

    function wireDownloads() {
      document.getElementById('download-json').addEventListener('click', () => {
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'traceability-audit.json';
        a.click();
        URL.revokeObjectURL(url);
      });

      document.getElementById('download-links').addEventListener('click', () => {
        const header = 'requirement_id,test_id\n';
        const rows = data.links.map(l => `${l.req},${l.test}`).join('\n');
        const blob = new Blob([header + rows], {type: 'text/csv'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'traceability-links.csv';
        a.click();
        URL.revokeObjectURL(url);
      });
    }

    function update() {
      renderReqTable();
      renderTestTable();
    }

    searchInput.addEventListener('input', update);
    statusFilter.addEventListener('change', update);
    showMatrix.addEventListener('change', () => {
      matrixSection.style.display = showMatrix.checked ? 'block' : 'none';
    });
    showTests.addEventListener('change', () => {
      testsSection.style.display = showTests.checked ? 'block' : 'none';
    });

    renderCards();
    renderMatrix();
    wireDownloads();
    update();
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a traceability audit HTML report from requirement items and test annotations.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--root", default=".", help="Project root containing item directories.")
    parser.add_argument(
        "--display-root",
        default=".",
        help="Display label for the project root (kept relative for audit reports).",
    )
    parser.add_argument(
        "--req-dir",
        action="append",
        default=[],
        help="Requirement item directory, relative to root. Can be repeated.",
    )
    parser.add_argument(
        "--test-dir",
        action="append",
        default=[],
        help="Test item directory (Doorstop YAML), relative to root. Can be repeated.",
    )
    parser.add_argument(
        "--test-scan-dir",
        action="append",
        default=[],
        help="Directory to scan for in-test HODOR metadata comments. Can be repeated.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: <root>/visual/traceability_audit.html).",
    )
    parser.add_argument("--title", default="Traceability Audit", help="Report title.")
    parser.add_argument(
        "--subtitle",
        default="Audit-focused view of requirement coverage and test linkage.",
        help="Report subtitle.",
    )
    return parser.parse_args()


def load_items(root: Path, rel_dirs: list[str], label: str) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    for rel_dir in rel_dirs:
        dir_path = (root / rel_dir).resolve()
        if not dir_path.exists():
            raise FileNotFoundError(f"{label} directory not found: {dir_path}")
        for ext in ("*.yml", "*.yaml"):
            for item_file in sorted(dir_path.rglob(ext)):
                if item_file.name in SKIP_NAMES:
                    continue
                data = yaml.safe_load(item_file.read_text(encoding="utf-8")) or {}
                uid = str(data.get("uid") or item_file.stem)
                if uid in seen:
                    raise ValueError(f"Duplicate item id '{uid}' in {item_file}")
                seen.add(uid)
                text = data.get("text") or data.get("title") or ""
                if not isinstance(text, str):
                    text = str(text)
                links = data.get("links") or []
                if isinstance(links, str):
                    links = [links]
                elif not isinstance(links, list):
                    links = []
                links = [str(link) for link in links]
                try:
                    rel_path = item_file.relative_to(root)
                except ValueError:
                    rel_path = item_file
                items.append(
                    {
                        "id": uid,
                        "text": text.rstrip(),
                        "links": links,
                        "path": str(rel_path),
                    }
                )
    return items


def split_list(value: str) -> list[str]:
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]


def iter_scan_files(dir_path: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(dir_path):
        dirs[:] = sorted(d for d in dirs if d not in SCAN_SKIP_DIRS)
        for name in sorted(names):
            files.append(Path(root) / name)
    return files


def parse_hodor_blocks(lines: list[str], path_label: str) -> list[dict]:
    blocks: list[dict] = []
    current: dict | None = None
    for line_no, line in enumerate(lines, start=1):
        match = DIRECTIVE_RE.match(line)
        if match:
            directive = match.group(1).strip()
            value = match.group(2).strip()
            if current is None:
                current = {"id": None, "reqs": [], "refs": [], "text": [], "start_line": line_no}
            if directive == "HODOR-ID":
                current["id"] = value
            elif directive == "HODOR-REQS":
                current["reqs"].extend(split_list(value))
            elif directive in {"HODOR-REF", "HODOR-REFS"}:
                current["refs"].extend(split_list(value))
            elif directive == "HODOR-TEXT":
                if value:
                    current["text"].append(value)
            else:
                raise ValueError(f"Unknown HODOR directive '{directive}' in {path_label}:{line_no}")
            continue
        if current is not None:
            blocks.append(current)
            current = None
    if current is not None:
        blocks.append(current)
    return blocks


def load_test_annotations(root: Path, rel_dirs: list[str]) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    for rel_dir in rel_dirs:
        dir_path = (root / rel_dir).resolve()
        if not dir_path.exists():
            raise FileNotFoundError(f"Test scan directory not found: {dir_path}")
        for file_path in iter_scan_files(dir_path):
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            blocks = parse_hodor_blocks(content.splitlines(), str(file_path))
            if not blocks:
                continue
            try:
                rel_path = file_path.relative_to(root)
            except ValueError:
                rel_path = file_path
            rel_label = str(rel_path)
            for block in blocks:
                reqs = block["reqs"]
                if not reqs:
                    raise ValueError(f"Missing HODOR-REQS in {rel_label}:{block['start_line']}")
                test_id = block["id"] or f"{rel_label}#L{block['start_line']}"
                if test_id in seen:
                    raise ValueError(f"Duplicate test id '{test_id}' in {rel_label}")
                seen.add(test_id)
                text = "\n".join(block["text"]).strip()
                if not text:
                    text = f"Traceability marker in {rel_label}"
                items.append(
                    {
                        "id": test_id,
                        "text": text,
                        "links": reqs,
                        "path": rel_label,
                        "refs": block["refs"],
                    }
                )
    return items


def extract_refs(text: str) -> list[str]:
    refs: list[str] = []
    lines = [line.rstrip() for line in text.splitlines()]
    in_refs = False
    for line in lines:
        if line.strip() == "References:":
            in_refs = True
            continue
        if in_refs:
            if not line.strip():
                break
            if line.strip().startswith("- "):
                refs.append(line.strip()[2:])
            else:
                break
    return refs


def build_payload(
    root: Path,
    req_dirs: list[str],
    test_item_dirs: list[str],
    test_scan_dirs: list[str],
    display_root: str,
) -> dict:
    reqs = load_items(root, req_dirs, "Requirement")
    item_tests = load_items(root, test_item_dirs, "Test") if test_item_dirs else []
    scan_tests = load_test_annotations(root, test_scan_dirs) if test_scan_dirs else []
    tests = item_tests + scan_tests

    req_map = {r["id"]: r for r in reqs}
    test_map = {t["id"]: t for t in tests}

    seen_test_ids: set[str] = set()
    for test in tests:
        test_id = test["id"]
        if test_id in seen_test_ids:
            raise ValueError(f"Duplicate test id '{test_id}'")
        seen_test_ids.add(test_id)
        if "refs" not in test:
            test["refs"] = extract_refs(test["text"])

    link_set: set[tuple[str, str]] = set()
    for test in tests:
        for req_id in test["links"]:
            if req_id in req_map:
                link_set.add((req_id, test["id"]))
    for req in reqs:
        for test_id in req["links"]:
            if test_id in test_map:
                link_set.add((req["id"], test_id))

    req_to_tests = {req_id: [] for req_id in req_map}
    test_to_reqs = {test_id: [] for test_id in test_map}
    for req_id, test_id in sorted(link_set):
        req_to_tests[req_id].append(test_id)
        test_to_reqs[test_id].append(req_id)

    for req in reqs:
        req["tests"] = sorted(req_to_tests.get(req["id"], []))
        req["status"] = "linked" if req["tests"] else "unlinked"
    for test in tests:
        test["reqs"] = sorted(test_to_reqs.get(test["id"], []))
        test["status"] = "linked" if test["reqs"] else "unlinked"

    summary = {
        "requirements_total": len(reqs),
        "tests_total": len(tests),
        "links_total": len(link_set),
        "requirements_linked": sum(1 for r in reqs if r["tests"]),
        "requirements_unlinked": sum(1 for r in reqs if not r["tests"]),
        "tests_linked": sum(1 for t in tests if t["reqs"]),
        "tests_unlinked": sum(1 for t in tests if not t["reqs"]),
    }
    summary["coverage_pct"] = (
        round(100.0 * summary["requirements_linked"] / summary["requirements_total"], 1)
        if summary["requirements_total"]
        else 0.0
    )

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "source_root": display_root,
        "summary": summary,
        "requirements": reqs,
        "tests": tests,
        "links": [{"req": req_id, "test": test_id} for req_id, test_id in sorted(link_set)],
    }


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    req_dirs = args.req_dir or DEFAULT_REQ_DIRS
    test_item_dirs = args.test_dir or DEFAULT_TEST_DIRS
    test_scan_dirs = args.test_scan_dir or DEFAULT_TEST_SCAN_DIRS
    out_path = Path(args.out) if args.out else root / "visual" / "traceability_audit.html"

    payload = build_payload(root, req_dirs, test_item_dirs, test_scan_dirs, args.display_root)
    data_json = json.dumps(payload, ensure_ascii=True).replace("</", "<\\/")
    html = (
        TEMPLATE.replace("__DATA_JSON__", data_json)
        .replace("__SOURCE_ROOT__", payload["source_root"])
        .replace("__GENERATED_AT__", payload["generated_at"])
        .replace("__TITLE__", args.title)
        .replace("__SUBTITLE__", args.subtitle)
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
