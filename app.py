from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.fortran_parser import FortranParser
from src.c_parser import CHeaderParser
from src.validator import Validator


app = FastAPI(title="Fortran-C Interface Validator")


class ValidationRequest(BaseModel):
    fortran_code: str
    c_code: str


def validate_source(fortran_source: str, c_source: str) -> dict:
    fp = FortranParser()
    cp = CHeaderParser()

    fortran_funcs = fp.parse(fortran_source)
    c_funcs = cp.parse(c_source)

    v = Validator()
    result = v.validate(fortran_funcs, c_funcs)

    result["fortran_functions"] = [
        {
            "name": f.name,
            "return_type": f.return_type,
            "params": [
                {"name": p.name, "type": p.base_type, "mode": p.passing_mode.value}
                for p in f.params
            ],
            "line": f.line_no,
        }
        for f in fortran_funcs
    ]
    result["c_functions"] = [
        {
            "name": f.name,
            "return_type": f.return_type,
            "params": [
                {"name": p.name, "type": p.base_type, "mode": p.passing_mode.value}
                for p in f.params
            ],
            "line": f.line_no,
        }
        for f in c_funcs
    ]

    return result


@app.post("/api/validate")
def api_validate(payload: ValidationRequest):
    if not payload.fortran_code.strip() or not payload.c_code.strip():
        raise HTTPException(status_code=400, detail="Both Fortran and C code are required.")

    return validate_source(payload.fortran_code, payload.c_code)


@app.get("/", response_class=HTMLResponse)
def index():
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fortran-C Interface Validator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #0b1116;
      --panel: #121b22;
      --panel-2: #18232c;
      --text: #e6eef5;
      --muted: #9fb0bf;
      --accent: #48d0c5;
      --accent-2: #f2c14e;
      --danger: #ff6b6b;
      --ok: #7bd389;
      --border: #22303b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Space Grotesk", system-ui, -apple-system, sans-serif;
      color: var(--text);
      background: radial-gradient(1200px 700px at 10% -10%, #18303a 0%, #0b1116 55%),
                  radial-gradient(900px 600px at 110% 0%, #1a2b24 0%, #0b1116 60%);
    }
    header {
      padding: 32px 24px 12px;
      text-align: center;
    }
    header h1 {
      margin: 0;
      font-size: 28px;
      letter-spacing: 0.4px;
    }
    header p {
      margin: 10px 0 0;
      color: var(--muted);
    }
    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 20px 24px 48px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }
    .panel {
      background: linear-gradient(180deg, rgba(24,35,44,0.95), rgba(18,27,34,0.95));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      min-height: 320px;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
    }
    label {
      display: block;
      font-weight: 600;
      margin-bottom: 8px;
    }
    textarea {
      width: 100%;
      height: 250px;
      resize: vertical;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      background: #0f151b;
      color: var(--text);
      font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
      line-height: 1.4;
    }
    .actions {
      display: flex;
      gap: 12px;
      align-items: center;
      margin: 18px 0 8px;
    }
    button {
      background: var(--accent);
      color: #041516;
      border: none;
      border-radius: 10px;
      padding: 10px 16px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.12s ease, box-shadow 0.12s ease;
      box-shadow: 0 8px 24px rgba(72, 208, 197, 0.25);
    }
    button:hover { transform: translateY(-1px); }
    button.secondary {
      background: transparent;
      color: var(--text);
      border: 1px solid var(--border);
      box-shadow: none;
    }
    .results {
      margin-top: 18px;
      padding: 18px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--panel);
    }
    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }
    .card {
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px;
      text-align: center;
    }
    .card .label {
      color: var(--muted);
      font-size: 12px;
    }
    .card .value {
      font-size: 18px;
      font-weight: 700;
    }
    .card.good {
      border-color: rgba(123, 211, 137, 0.5);
    }
    .card.warn {
      border-color: rgba(242, 193, 78, 0.5);
    }
    .card.bad {
      border-color: rgba(255, 107, 107, 0.5);
    }
    .health {
      display: grid;
      gap: 8px;
      margin-bottom: 14px;
    }
    .bar {
      height: 10px;
      border-radius: 999px;
      background: #0f151b;
      border: 1px solid var(--border);
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--ok), var(--accent));
      width: 0%;
      transition: width 0.2s ease;
    }
    .breakdown {
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 10px;
      margin: 16px 0;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: #0f151b;
      font-size: 12px;
      color: var(--muted);
    }
    .pill .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-2);
    }
    .list {
      display: grid;
      gap: 10px;
    }
    .item {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      background: #0f151b;
    }
    .item.error { border-color: rgba(255, 107, 107, 0.5); }
    .item.ok { border-color: rgba(123, 211, 137, 0.5); }
    .tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
      letter-spacing: 0.2px;
      text-transform: uppercase;
    }
    .tag.error { background: rgba(255, 107, 107, 0.2); color: var(--danger); }
    .tag.ok { background: rgba(123, 211, 137, 0.2); color: var(--ok); }
    pre {
      background: #0f151b;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      overflow: auto;
      font-size: 12px;
      color: var(--muted);
    }
    details {
      margin-top: 18px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: var(--panel-2);
      padding: 10px 12px;
    }
    summary {
      cursor: pointer;
      font-weight: 600;
      color: var(--text);
      list-style: none;
    }
    summary::-webkit-details-marker {
      display: none;
    }
    summary::after {
      content: "▸";
      float: right;
      color: var(--muted);
    }
    details[open] summary::after {
      content: "▾";
    }
    .hidden { display: none; }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      .summary { grid-template-columns: repeat(2, minmax(140px, 1fr)); }
      .breakdown { grid-template-columns: repeat(2, minmax(140px, 1fr)); }
    }
  </style>
</head>
<body>
  <header>
    <h1>Fortran-C Interface Validator</h1>
    <p>Paste your Fortran and C declarations, validate, and inspect mismatches.</p>
  </header>
  <main class="container">
    <section class="grid">
      <div class="panel">
        <label for="fortran">Fortran (BIND(C))</label>
        <textarea id="fortran" placeholder="Paste Fortran source here..."></textarea>
      </div>
      <div class="panel">
        <label for="c">C Header</label>
        <textarea id="c" placeholder="Paste C header here..."></textarea>
      </div>
    </section>

    <div class="actions">
      <button id="validate">Validate</button>
      <button id="clear" class="secondary">Clear</button>
      <span id="status" style="color: var(--muted);"></span>
    </div>

    <section id="results" class="results hidden">
      <div class="health" id="health"></div>
      <div class="summary" id="summary"></div>
      <div class="breakdown" id="breakdown"></div>
      <div class="list" id="issues"></div>
      <details>
        <summary>Raw JSON</summary>
        <pre id="raw"></pre>
      </details>
    </section>
  </main>

  <script>
    const statusEl = document.getElementById("status");
    const resultEl = document.getElementById("results");
    const summaryEl = document.getElementById("summary");
    const issuesEl = document.getElementById("issues");
    const healthEl = document.getElementById("health");
    const breakdownEl = document.getElementById("breakdown");
    const rawEl = document.getElementById("raw");

    const formatCard = (label, value, tone = "") => {
      return `
        <div class="card ${tone}">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
        </div>
      `;
    };

    const formatPill = (label, value) => {
      return `
        <div class="pill">
          <span class="dot"></span>
          ${label}: <strong style="color: var(--text);">${value}</strong>
        </div>
      `;
    };

    const renderResult = (data) => {
      const s = data.summary || {};
      const matched = s.matched ?? 0;
      const clean = s.clean ?? 0;
      const errors = s.errors ?? 0;
      const warnings = s.warnings ?? 0;
      const cleanRate = matched > 0 ? Math.round((clean / matched) * 100) : 0;

      const unmatchedFortran = (data.unmatched_fortran || []).length;
      const unmatchedC = (data.unmatched_c || []).length;

      summaryEl.innerHTML = [
        formatCard("Fortran", s.total_fortran ?? 0),
        formatCard("C", s.total_c ?? 0),
        formatCard("Matched", matched),
        formatCard("Clean", clean, clean === matched ? "good" : "warn"),
        formatCard("Errors", errors, errors > 0 ? "bad" : "good"),
        formatCard("Warnings", warnings, warnings > 0 ? "warn" : "good"),
        formatCard("Unmatched F", unmatchedFortran, unmatchedFortran > 0 ? "warn" : "good"),
        formatCard("Unmatched C", unmatchedC, unmatchedC > 0 ? "warn" : "good")
      ].join("");

      healthEl.innerHTML = `
        <div style="display:flex; justify-content: space-between; align-items: center;">
          <div style="font-weight: 600;">Compatibility score</div>
          <div style="color: var(--muted);">${cleanRate}% clean</div>
        </div>
        <div class="bar"><div class="bar-fill" style="width: ${cleanRate}%;"></div></div>
      `;

      const mismatches = data.mismatches || [];
      const kindCounts = mismatches.reduce((acc, m) => {
        const key = (m.kind || "unknown").toUpperCase();
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {});

      const breakdownItems = Object.keys(kindCounts).length > 0
        ? Object.entries(kindCounts).map(([k, v]) => formatPill(k, v)).join("")
        : formatPill("OK", "No mismatches");
      breakdownEl.innerHTML = breakdownItems;

      if (mismatches.length === 0) {
        issuesEl.innerHTML = `
          <div class="item ok">
            <span class="tag ok">OK</span>
            All matched interfaces are compatible.
          </div>
        `;
      } else {
        issuesEl.innerHTML = mismatches.map((m) => {
          return `
            <div class="item error">
              <span class="tag error">${m.kind || "error"}</span>
              <div style="margin-top: 6px; font-weight: 600;">${m.function}</div>
              <div style="color: var(--muted); margin-top: 4px;">${m.description}</div>
              <div style="margin-top: 4px;">Fortran: ${m.fortran_value} | C: ${m.c_value}</div>
            </div>
          `;
        }).join("");
      }

      rawEl.textContent = JSON.stringify(data, null, 2);
      resultEl.classList.remove("hidden");
    };

    document.getElementById("validate").addEventListener("click", async () => {
      const fortran = document.getElementById("fortran").value;
      const c = document.getElementById("c").value;

      statusEl.textContent = "Validating...";
      try {
        const resp = await fetch("/api/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fortran_code: fortran, c_code: c })
        });

        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.detail || "Validation failed");
        }

        const data = await resp.json();
        renderResult(data);
        statusEl.textContent = "Done";
      } catch (err) {
        statusEl.textContent = err.message;
      }
    });

    document.getElementById("clear").addEventListener("click", () => {
      document.getElementById("fortran").value = "";
      document.getElementById("c").value = "";
      statusEl.textContent = "";
      resultEl.classList.add("hidden");
      breakdownEl.innerHTML = "";
      healthEl.innerHTML = "";
    });
  </script>
</body>
</html>
    """
    return HTMLResponse(content=html)
