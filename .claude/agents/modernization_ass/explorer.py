#!/usr/bin/env python3
"""
explorer.py — Repo analyzer with per-area folders.
Outputs:
- modernization_artifacts/global/{INVENTORY.json, SUMMARY.md, STACK_OVERVIEW.md}
- modernization_artifacts/<area>/{INVENTORY.json, SUMMARY.md, NEXT_STEPS.md}
- modernization_artifacts/data/DATA_OBJECTS.csv (tables/views/procs/ORM entities)

Usage:
    python explorer.py --repo . --out modernization_artifacts
"""

import argparse, os, re, json, csv
from pathlib import Path

# -----------------------------
# Configuration & Heuristics
# -----------------------------
AREAS = {
    "data": [".sql", ".parquet", "dags/", "models/"],
    "backend": [".py", ".java", ".cs", "services/"],
    "frontend": [".js", ".ts", ".jsx", ".tsx", "angular.json", "vite.config"],
    "devops": ["Dockerfile", "docker-compose", ".github/workflows", ".gitlab-ci.yml", "terraform/"],
    "testing": ["tests/", "pytest.ini", "jest.config"],
}

LANGUAGES = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".cs": "C#",
    ".sql": "SQL",
    ".json": "JSON",
    ".yml": "YAML",
    ".yaml": "YAML",
}

CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs"}

DEFAULT_EXCLUDES = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "modernization_artifacts"
}

# SQL object detection (tolerant)
RE_CREATE_TABLE = re.compile(r"create\s+table\s+(if\s+not\s+exists\s+)?([`\"[]?\w+([.`\"]\w+)*[`\"\\]]?)", re.IGNORECASE)
RE_CREATE_VIEW  = re.compile(r"create\s+(or\s+replace\s+)?view\s+([`\"[]?\w+([.`\"]\w+)*[`\"\\]]?)", re.IGNORECASE)
RE_CREATE_PROC  = re.compile(r"create\s+(or\s+replace\s+)?(procedure|function)\s+([`\"[]?\w+([.`\"]\w+)*[`\"\\]]?)", re.IGNORECASE)

# Django ORM model detection
RE_DJANGO_MODEL = re.compile(r"class\s+([A-Za-z_]\w*)\s*\(\s*models\.Model\s*\)\s*:", re.MULTILINE)
RE_INSTALLED_APPS = re.compile(r"INSTALLED_APPS\s*=\s*\[([^\]]*)\]", re.DOTALL)
RE_DJANGO_SETTINGS_MODULE = re.compile(r"DJANGO_SETTINGS_MODULE", re.IGNORECASE)

# -----------------------------
# Helpers
# -----------------------------
def detect_area(path: str):
    p = path.lower()
    for area, patterns in AREAS.items():
        for pat in patterns:
            if pat.lower() in p:
                return area
    return None

def detect_language(filename: str):
    return LANGUAGES.get(Path(filename).suffix.lower())

def should_exclude(path_parts):
    for part in path_parts:
        if part in DEFAULT_EXCLUDES:
            return True
    return False

def read_text(path: Path, limit: int | None = None) -> str:
    try:
        if limit:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(limit)
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def read_small_code(path: Path, max_bytes: int = 4000) -> str:
    if Path(path).suffix.lower() not in CODE_EXTS and Path(path).suffix.lower() != ".py":
        return ""
    return read_text(path, limit=max_bytes)

def parse_sql_objects(sql_text: str, source_rel: str):
    objs = {"tables": [], "views": [], "procedures": []}
    for m in RE_CREATE_TABLE.finditer(sql_text):
        objs["tables"].append({"name": m.group(2), "source": source_rel})
    for m in RE_CREATE_VIEW.finditer(sql_text):
        objs["views"].append({"name": m.group(2), "source": source_rel})
    for m in RE_CREATE_PROC.finditer(sql_text):
        objs["procedures"].append({"name": m.group(3), "source": source_rel})
    return objs

def detect_django_entities(py_text: str, source_rel: str):
    entities = []
    for m in RE_DJANGO_MODEL.finditer(py_text):
        entities.append({"entity": m.group(1), "source": source_rel})
    return entities

def detect_django_settings(py_text: str, source_rel: str):
    hints = []
    if RE_INSTALLED_APPS.search(py_text):
        hints.append(f"found 'INSTALLED_APPS' in {source_rel}")
    if RE_DJANGO_SETTINGS_MODULE.search(py_text):
        hints.append(f"found 'DJANGO_SETTINGS_MODULE' reference in {source_rel}")
    return hints

def detect_frameworks_from_file(repo_root: Path, rel_path: str, content: str):
    ev = {}
    name = os.path.basename(rel_path)
    suffix = Path(rel_path).suffix.lower()

    # Django filenames
    if name in {"manage.py", "settings.py"}:
        ev.setdefault("Django", []).append(f"found '{name}' in {rel_path}")

    # Django settings content
    if name.endswith("settings.py") and content:
        for hint in detect_django_settings(content, rel_path):
            ev.setdefault("Django", []).append(hint)

    # Python imports
    if suffix == ".py" and content:
        if "from flask import" in content:
            ev.setdefault("Flask", []).append(f"found 'from flask import' in {rel_path}")
        if "from fastapi import" in content:
            ev.setdefault("FastAPI", []).append(f"found 'from fastapi import' in {rel_path}")
        if "from airflow import" in content:
            ev.setdefault("Airflow", []).append(f"found 'from airflow import' in {rel_path}")

    # React/Next by extensions + package.json
    if suffix in {".jsx", ".tsx"}:
        ev.setdefault("React", []).append(f"found '{suffix}' file {rel_path}")

    if name == "package.json":
        try:
            pkg = json.loads((repo_root / rel_path).read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "react" in deps:
                ev.setdefault("React", []).append(f"found 'react' dependency in {rel_path}")
            if "next" in deps:
                ev.setdefault("Next.js", []).append(f"found 'next' dependency in {rel_path}")
            if "@angular/core" in deps:
                ev.setdefault("Angular", []).append(f"found '@angular/core' dependency in {rel_path}")
            if "vue" in deps:
                ev.setdefault("Vue", []).append(f"found 'vue' dependency in {rel_path}")
        except Exception:
            pass

    if name == "angular.json":
        ev.setdefault("Angular", []).append(f"found 'angular.json' in {rel_path}")
    if name in {"vue.config.js", "App.vue"}:
        ev.setdefault("Vue", []).append(f"found '{name}' in {rel_path}")

    return ev

def ensure_area_dirs(base_out: Path):
    (base_out / "global").mkdir(parents=True, exist_ok=True)
    for area in AREAS:
        (base_out / area).mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def write_md(path: Path, lines: list[str]):
    path.write_text("\n".join(lines), encoding="utf-8")

def write_data_objects_csv(path: Path, tables, views, procs, entities):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["type", "name_or_entity", "source_file"])
        for t in tables:
            w.writerow(["table", t["name"], t["source"]])
        for v in views:
            w.writerow(["view", v["name"], v["source"]])
        for p in procs:
            w.writerow(["procedure_or_function", p["name"], p["source"]])
        for e in entities:
            w.writerow(["orm_entity", e["entity"], e["source"]])

def summarize_languages(languages: dict):
    if not languages:
        return ["- None"]
    return [f"- {lang}: {count} files" for lang, count in sorted(languages.items(), key=lambda x: (-x[1], x[0]))]

def summarize_frameworks(frameworks: dict):
    lines = []
    if not frameworks:
        return ["- None"]
    for fw, evidences in frameworks.items():
        lines.append(f"- {fw}")
        for ev in evidences:
            lines.append(f"  - {ev}")
    return lines

def per_area_next_steps(area: str, metrics: dict, t_count: int, v_count: int, p_count: int, e_count: int):
    steps = [f"# Next Steps — {area.title()}", ""]
    if area == "data":
        if t_count or e_count:
            steps.append(f"- Validate schema mapping: {t_count} SQL tables + {e_count} ORM entities detected.")
        if v_count or p_count:
            steps.append(f"- Review {v_count} views and {p_count} procedures/functions for portability.")
        steps.append("- Identify DB engines and dialect-specific features.")
        steps.append("- Define DDL migration strategy and data validation checks.")
    elif area == "backend":
        steps.append("- Review dependencies, API surface, and service boundaries.")
        steps.append("- Check framework versions and deprecations.")
        steps.append("- Add/verify unit and integration tests.")
    elif area == "frontend":
        steps.append("- Validate build config (bundler, SSR/CSR), routes and env handling.")
        steps.append("- Check dependency health and security advisories.")
    elif area == "devops":
        steps.append("- Inspect CI/CD pipelines, IaC modules, and deployment targets.")
        steps.append("- Ensure secrets are not committed and policies are enforced.")
    elif area == "testing":
        steps.append("- Establish minimal test coverage and CI gating.")
    return steps

# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Path to repo")
    parser.add_argument("--out", default="modernization_artifacts", help="Output folder")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    outdir = Path(args.out).resolve()
    self_name = Path(__file__).name

    ensure_area_dirs(outdir)

    # Global accumulators
    artifacts_by_area: dict[str, list] = {a: [] for a in AREAS}
    metrics = {a: 0 for a in AREAS}
    languages = {}
    frameworks = {}

    sql_tables, sql_views, sql_procs, orm_entities = [], [], [], []

    # Walk
    for root, dirs, files in os.walk(repo):
        # prune excluded dirs
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES]

        for f in files:
            full = Path(root) / f
            rel = str(full.relative_to(repo))

            # exclude self & outputs
            parts = set(Path(rel).parts)
            if should_exclude(parts) or f == self_name:
                continue

            area = detect_area(rel)
            if not area:
                continue

            lang = detect_language(f)
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

            artifacts_by_area[area].append({"id": f"{area}:{rel}", "area": area, "location": rel})
            metrics[area] += 1

            suffix = Path(rel).suffix.lower()

            # data-specific parsing
            if suffix == ".sql":
                sql_text = read_text(full)
                objs = parse_sql_objects(sql_text, rel)
                sql_tables.extend(objs["tables"])
                sql_views.extend(objs["views"])
                sql_procs.extend(objs["procedures"])

            if suffix == ".py" and ("models.py" in rel or "models_" in Path(rel).name):
                py_text = read_text(full)
                ents = detect_django_entities(py_text, rel)
                orm_entities.extend(ents)

            # framework evidence (code-only)
            content = read_small_code(full)
            file_ev = detect_frameworks_from_file(repo, rel, content)
            for fw, evs in file_ev.items():
                frameworks.setdefault(fw, []).extend(evs)

    # Deduplicate & cap evidences
    for fw in list(frameworks.keys()):
        seen, uniq = set(), []
        for e in frameworks[fw]:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        frameworks[fw] = uniq[:8]

    # -----------------------------
    # Write GLOBAL outputs
    # -----------------------------
    global_dir = outdir / "global"
    global_dir.mkdir(parents=True, exist_ok=True)

    global_inventory = {
        "metrics": metrics,
        "languages": languages,
        "frameworks": frameworks,
        "data_insights": {
            "sql_objects": {
                "tables": sql_tables,
                "views": sql_views,
                "procedures": sql_procs,
            },
            "orm_entities": orm_entities
        }
    }
    write_json(global_dir / "INVENTORY.json", global_inventory)

    summary_lines = ["# Project Summary", ""]
    for area, count in metrics.items():
        summary_lines.append(f"- {area}: {count} artifacts detected")
    summary_lines += ["", "## Languages detected"] + summarize_languages(languages)
    summary_lines += ["", "## Frameworks detected (with evidence)"] + summarize_frameworks(frameworks)
    summary_lines += ["", "## Data objects (parsed)"]
    summary_lines.append(f"- SQL Tables: {len(sql_tables)}")
    summary_lines.append(f"- SQL Views: {len(sql_views)}")
    summary_lines.append(f"- SQL Procedures/Functions: {len(sql_procs)}")
    summary_lines.append(f"- ORM Entities (Django models): {len(orm_entities)}")
    write_md(global_dir / "SUMMARY.md", summary_lines)

    stack_lines = ["# Stack Overview", ""]
    stack_lines.append("## Area coverage")
    for a, c in metrics.items():
        stack_lines.append(f"- {a}: {c} artifacts")
    stack_lines += ["", "## Languages"] + summarize_languages(languages)
    stack_lines += ["", "## Frameworks"] + ([f"- {k}" for k in frameworks.keys()] or ["- None"])
    stack_lines += ["", "## Notes", "- This is a static offline scan; frameworks are inferred via filenames/imports/deps."]
    write_md(global_dir / "STACK_OVERVIEW.md", stack_lines)

    # -----------------------------
    # Write PER-AREA outputs
    # -----------------------------
    for area, artifacts in artifacts_by_area.items():
        area_dir = outdir / area
        area_dir.mkdir(parents=True, exist_ok=True)

        # Area inventory
        write_json(area_dir / "INVENTORY.json", {"artifacts": artifacts})

        # Area summary
        area_summary = [f"# {area.title()} Summary", ""]
        area_summary.append(f"- artifacts: {len(artifacts)}")
        if area == "data":
            area_summary += [
                "",
                "## Parsed SQL objects",
                f"- tables: {len(sql_tables)}",
                f"- views: {len(sql_views)}",
                f"- procedures/functions: {len(sql_procs)}",
                "## ORM entities (Django)",
                f"- entities: {len(orm_entities)}",
            ]
        write_md(area_dir / "SUMMARY.md", area_summary)

        # Area next steps
        steps = per_area_next_steps(
            area,
            metrics,
            t_count=len(sql_tables),
            v_count=len(sql_views),
            p_count=len(sql_procs),
            e_count=len(orm_entities),
        )
        write_md(area_dir / "NEXT_STEPS.md", steps)

    # DATA extra: CSV with consolidated objects
    data_dir = outdir / "data"
    if sql_tables or sql_views or sql_procs or orm_entities:
        write_data_objects_csv(
            data_dir / "DATA_OBJECTS.csv",
            sql_tables, sql_views, sql_procs, orm_entities
        )

    print(f"Analysis generated under: {outdir}")

if __name__ == "__main__":
    main()
