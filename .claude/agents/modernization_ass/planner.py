#!/usr/bin/env python3
"""
planner.py — Build a modernization plan from:
- inventory: modernization_artifacts/global/INVENTORY.json
- proposals: FEATURE_PROPOSALS.md (or .txt/.yaml/.json)

Usage:
    python planner.py --inventory modernization_artifacts/global/INVENTORY.json --goals FEATURE_PROPOSALS.md
Outputs:
    modernization_artifacts/global/MODERNIZATION_PLAN.md
    modernization_artifacts/global/ROADMAP.csv
"""

import argparse, json, re, csv, sys
from pathlib import Path

try:
    import yaml  # optional for .yaml goals
except Exception:
    yaml = None

# --------------------------
# Keywords & heuristics
# --------------------------
AREA_KEYWORDS = {
    "data":    ["table", "view", "materialized", "index", "warehouse", "lake", "etl", "ingest", "analytics", "kpi", "report", "bi", "metric", "postgres", "postgresql", "sql", "dbt"],
    "backend": ["api", "service", "endpoint", "auth", "login", "cart", "checkout", "order", "payment", "websocket", "sse", "cron", "job", "worker", "fastapi", "django", "flask", "celery"],
    "frontend":["react", "next", "spa", "component", "ui", "ux", "route", "page", "wishlist", "search", "filter", "sort", "pagination", "checkout ui"],
    "devops":  ["docker", "k8s", "kubernetes", "terraform", "iac", "pipeline", "ci", "cd", "deploy", "secrets", "env", "monitor", "logging", "tracing", "observability", "sentry", "prometheus", "grafana"],
    "testing": ["test", "coverage", "unit", "integration", "e2e", "cypress", "pytest", "jest", "contract", "smoke"],
}

# If the proposal line already tags the area like [Backend], [Frontend], etc.
AREA_TAGS = {
    "[data]": "data", "[backend]": "backend", "[frontend]": "frontend", "[devops]": "devops", "[testing]": "testing"
}

# Phase mapping rules. Priority in proposals wins; else heuristics.
PHASE_FROM_PRIORITY = {"high": "Now", "medium": "Next", "low": "Later"}
PHASE_RULES = [
    (r"\brefactor|cleanup|lint|hardening|security\b", "Now"),
    (r"\btest|coverage|qa|ci\b", "Now"),
    (r"\bmigrate|upgrade|bump|deploy|cd\b", "Next"),
    (r"\bscale|performance|optimi[sz]e|cache\b", "Later"),
]

# Stack expectations for this e-commerce (still works if inventory differs)
EXPECTED_STACK = {"backend": {"FastAPI"}, "frontend": {"React"}, "database": {"Postgres", "PostgreSQL", "postgres"}}

# --------------------------
# Parsers
# --------------------------
def load_inventory(path: Path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "metrics"      : data.get("metrics", {}),
        "languages"    : data.get("languages", {}),
        "frameworks"   : data.get("frameworks", {}),  # {fw: [evidence...]}
        "data_insights": data.get("data_insights", {"sql_objects": {"tables": [], "views": [], "procedures": []}, "orm_entities": []}),
    }

def load_goals(path: Path):
    p = Path(path)
    if not p.exists():
        print(f"[planner] goals file not found: {p}", file=sys.stderr)
        return []
    text = p.read_text(encoding="utf-8", errors="ignore")
    items = []

    if p.suffix.lower() in {".yaml", ".yml"} and yaml:
        try:
            data = yaml.safe_load(text) or {}
            if isinstance(data, dict) and "goals" in data and isinstance(data["goals"], list):
                items = [str(x) for x in data["goals"]]
            elif isinstance(data, list):
                items = [str(x) for x in data]
        except Exception:
            pass
    elif p.suffix.lower() == ".json":
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "goals" in data and isinstance(data["goals"], list):
                items = [str(x) for x in data["goals"]]
            elif isinstance(data, list):
                items = [str(x) for x in data]
        except Exception:
            pass
    else:
        # md/txt: extract meaningful features, not individual lines
        lines = text.splitlines()
        current_feature = None
        current_section = None
        
        for i, line in enumerate(lines):
            s = line.strip()
            
            # Skip empty lines and pure formatting
            if not s or set(s) <= {"-", "*", "•", "#", "=", "-"}:
                continue
                
            # Extract feature titles (### Feature X: ...)
            if s.startswith("### Feature ") and ":" in s:
                current_feature = s
                items.append(s)
                continue
                
            # Extract main headings that represent features
            if s.startswith("## ") and not s.startswith("## Project") and not s.startswith("## Current") and not s.startswith("## Proposed"):
                # This might be a feature section
                if "feature" in s.lower() or "system" in s.lower() or "dashboard" in s.lower():
                    items.append(s)
                continue
                
            # Extract user stories (As a...)
            if s.startswith("As a ") and "I want" in s:
                if current_feature:
                    # Group with current feature
                    items.append(f"{current_feature}: {s}")
                else:
                    items.append(s)
                continue
                
            # Skip markdown formatting and short lines
            if len(s) < 10 or s.startswith("#") or s.startswith("**") or s.startswith("- ") or s.startswith("* "):
                continue
                
            # Skip common non-feature content
            skip_patterns = [
                "business value", "acceptance criteria", "user story", "rationale",
                "implementation", "sprints", "priority", "complexity", "roi",
                "high", "medium", "low", "clear", "moderate", "relatively"
            ]
            if any(pattern in s.lower() for pattern in skip_patterns):
                continue
                
            # Only add substantial content
            if len(s) >= 20 and not s.startswith("-") and not s.startswith("*"):
                items.append(s)

    # de-dup and filter
    seen, uniq = set(), []
    for it in items:
        key = it.strip()
        if key and key not in seen and len(key) >= 10:
            seen.add(key)
            uniq.append(key)
    return uniq

# --------------------------
# Classification
# --------------------------
def classify_area(goal: str):
    g = goal.lower()
    for tag, area in AREA_TAGS.items():
        if tag in g:
            return area
    scores = {a: 0 for a in AREA_KEYWORDS}
    for area, kws in AREA_KEYWORDS.items():
        for kw in kws:
            if kw in g:
                scores[area] += 1
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] == 0:
        # default bias: backend
        return "backend"
    return best[0]

def classify_phase(goal: str):
    # explicit priority markers like "(Priority: High)"
    m = re.search(r"priority\s*[:=]\s*(high|medium|low)", goal, re.IGNORECASE)
    if m:
        return PHASE_FROM_PRIORITY[m.group(1).lower()]
    g = goal.lower()
    for pat, phase in PHASE_RULES:
        if re.search(pat, g):
            return phase
    # business features often give ROI → Now
    if any(w in g for w in ["search", "wishlist", "checkout", "cart", "payment"]):
        return "Now"
    return "Next"

# --------------------------
# Rationale & alignment
# --------------------------
def frameworks_set(frameworks_dict):
    return set(frameworks_dict.keys())

def db_summary(data_insights):
    t = len(data_insights.get("sql_objects", {}).get("tables", []))
    v = len(data_insights.get("sql_objects", {}).get("views", []))
    p = len(data_insights.get("sql_objects", {}).get("procedures", []))
    e = len(data_insights.get("orm_entities", []))
    return t, v, p, e

def infer_db_engine(data_insights):
    # naive hints from object names or sources
    engines = set()
    for obj in (data_insights.get("sql_objects", {}).get("tables", []) +
                data_insights.get("sql_objects", {}).get("views", []) +
                data_insights.get("sql_objects", {}).get("procedures", [])):
        src = obj.get("source", "").lower()
        name = str(obj.get("name", "")).lower()
        if any(x in (src + name) for x in ["postgres", "postgresql", "pg_"]):
            engines.add("Postgres")
        if any(x in (src + name) for x in ["mysql", "maria"]):
            engines.add("MySQL")
        if "sqlite" in (src + name):
            engines.add("SQLite")
        if any(x in (src + name) for x in ["mssql", "sqlserver"]):
            engines.add("SQL Server")
    return engines or {"Unknown"}

def build_rationale(goal: str, inv: dict, area: str):
    langs = inv["languages"]
    fws   = inv["frameworks"]
    data  = inv["data_insights"]
    fwset = frameworks_set(fws)
    t, v, p, e = db_summary(data)

    bits = []
    # Backend rationale
    if area == "backend":
        if "Python" in langs:
            bits.append("Python present")
        backend_hits = [fw for fw in ["FastAPI", "Django", "Flask", "Express", "Spring"] if fw in fwset]
        if backend_hits:
            bits.append("Frameworks detected: " + ", ".join(backend_hits))
        # align vs expected (FastAPI)
        if "FastAPI" in fwset:
            bits.append("Aligned with expected target FastAPI")
        elif "Django" in fwset:
            bits.append("Currently Django; consider migration or integrate feature in Django")
    # Frontend
    if area == "frontend":
        fe_hits = [fw for fw in ["React", "Next.js", "Angular", "Vue"] if fw in fwset]
        if fe_hits:
            bits.append("Frontend stack: " + ", ".join(fe_hits))
        if "React" in EXPECTED_STACK["frontend"]:
            bits.append("Matches expected React stack")
    # Data
    if area == "data":
        engines = ", ".join(sorted(infer_db_engine(data)))
        bits.append(f"Data footprint: {t} tables / {v} views / {p} procs; {e} ORM entities")
        bits.append(f"DB engine hint: {engines}")
        if any(x in EXPECTED_STACK["database"] for x in engines.split(", ")):
            bits.append("Matches expected Postgres target")
    # DevOps
    if area == "devops":
        if inv["metrics"].get("devops", 0) > 0:
            bits.append("DevOps/IaC assets detected")
        else:
            bits.append("Few/no DevOps assets detected (add pipelines)")
    # Testing
    if area == "testing":
        if inv["metrics"].get("testing", 0) == 0:
            bits.append("No tests detected; prioritize coverage")
        else:
            bits.append("Tests present; verify CI gating")

    return "; ".join(bits) or "Based on current repository scan"

# --------------------------
# Main
# --------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True, help="Path to global INVENTORY.json")
    ap.add_argument("--goals", required=True, help="Path to FEATURE_PROPOSALS.md/.txt/.yaml/.json")
    ap.add_argument("--outdir", default="modernization_artifacts/global", help="Output folder for plan")
    args = ap.parse_args()

    inv = load_inventory(Path(args.inventory))
    goals = load_goals(Path(args.goals))
    if not goals:
        print("[planner] No goals parsed. Ensure the file has one item per line or a goals list.", file=sys.stderr)
        sys.exit(1)

    # classify & enrich
    plan = []
    for g in goals:
        area = classify_area(g)
        phase = classify_phase(g)
        why = build_rationale(g, inv, area)
        plan.append({"goal": g, "area": area, "phase": phase, "rationale": why})

    # sort by phase → area → goal
    phase_order = {"Now": 0, "Next": 1, "Later": 2}
    plan.sort(key=lambda x: (phase_order.get(x["phase"], 3), x["area"], x["goal"].lower()))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # ---------- Markdown ----------
    lines = ["# Modernization Plan", ""]
    # Summary
    lines.append("## Repository snapshot")
    m = inv["metrics"]
    lines.append("- Areas: " + ", ".join([f"{k}:{v}" for k, v in m.items()]))
    if inv["languages"]:
        lines.append("- Languages: " + ", ".join([f"{k}({v})" for k, v in inv["languages"].items()]))
    if inv["frameworks"]:
        lines.append("- Frameworks: " + ", ".join(inv["frameworks"].keys()))
    t, v, p, e = db_summary(inv["data_insights"])
    lines.append(f"- Data objects: tables={t}, views={v}, procs={p}, orm_entities={e}")
    lines.append("")

    # Alignment notice
    fwset = frameworks_set(inv["frameworks"])
    alignment = []
    if "FastAPI" in fwset:
        alignment.append("Backend aligned with FastAPI.")
    elif "Django" in fwset:
        alignment.append("Backend currently Django (feature work can continue; migration optional).")
    if "React" in fwset:
        alignment.append("Frontend aligned with React.")
    if alignment:
        lines.append("> " + " ".join(alignment))
        lines.append("")

    # Plan by phase
    for phase in ["Now", "Next", "Later"]:
        lines.append(f"## {phase}")
        any_item = False
        for it in plan:
            if it["phase"] == phase:
                any_item = True
                lines.append(f"- **[{it['area'].title()}]** {it['goal']}")
                lines.append(f"  - Rationale: {it['rationale']}")
        if not any_item:
            lines.append("- (none)")
        lines.append("")

    # Backlog by area
    lines.append("## Backlog by area")
    for area in ["frontend", "backend", "data", "devops", "testing"]:
        lines.append(f"### {area.title()}")
        any_area = False
        for it in plan:
            if it["area"] == area:
                any_area = True
                lines.append(f"- {it['goal']} ({it['phase']})")
        if not any_area:
            lines.append("- (none)")
        lines.append("")

    # Dependencies (simple inference)
    lines.append("## Dependencies & sequencing (heuristic)")
    deps = []
    # If wishlist/search exist → prefer auth/catalog readiness
    has_search = any("search" in it["goal"].lower() for it in plan)
    has_wishlist = any("wishlist" in it["goal"].lower() for it in plan)
    if has_search:
        deps.append("- Search requires product catalog endpoints & indexes.")
    if has_wishlist:
        deps.append("- Wishlist requires auth/session & product endpoints.")
    if any("real-time" in it["goal"].lower() or "websocket" in it["goal"].lower() for it in plan):
        deps.append("- Real-time inventory requires stock events & reliable DB transactions.")
    if any("analytics" in it["goal"].lower() for it in plan):
        deps.append("- Analytics requires stable event schema and ETL job schedule.")
    lines += (deps or ["- (none)"])
    lines.append("")

    md_path = outdir / "MODERNIZATION_PLAN.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # ---------- CSV ----------
    csv_path = outdir / "ROADMAP.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["phase", "area", "goal", "rationale"])
        for it in plan:
            w.writerow([it["phase"], it["area"], it["goal"], it["rationale"]])

    print(f"[planner] Plan generated:\n- {md_path}\n- {csv_path}")

if __name__ == "__main__":
    main()
