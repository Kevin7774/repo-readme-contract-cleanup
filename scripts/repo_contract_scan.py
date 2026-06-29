#!/usr/bin/env python3
"""Lightweight repository contract scanner.

This script produces a markdown hint report for README/API/deployment cleanup.
It intentionally avoids modifying files. Treat results as leads that need human or
code-agent confirmation before deletion.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

TEXT_EXTS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".env",
    ".example",
    ".md",
    ".sh",
    ".conf",
    ".ini",
    ".cfg",
    ".txt",
}

STALE_PATTERNS = [
    ("old_port_8020", re.compile(r"\b8020\b")),
    ("old_or_test_port_801x", re.compile(r"\b801[0-9]\b")),
    ("hardcoded_localhost", re.compile(r"127\.0\.0\.1|localhost")),
    ("mock_fake_demo", re.compile(r"\b(mock|fake|demo|dummy|placeholder|sample)\b", re.I)),
    ("todo_fixme", re.compile(r"\b(todo|fixme|hack|xxx)\b", re.I)),
]

API_STRING_RE = re.compile(r"['\"](/(?:api/)?[a-zA-Z0-9_./{}:-]+)['\"]")
FASTAPI_ROUTE_RE = re.compile(r"@(?:router|app)\.(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]")
ENV_READ_RE = re.compile(r"(?:os\.getenv|os\.environ\.get|os\.environ\[|env\(|getenv\()\s*[\[\(]?\s*['\"]([A-Z][A-Z0-9_]+)['\"]")
ENV_LINE_RE = re.compile(r"^([A-Z][A-Z0-9_]+)=", re.M)


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            path = Path(dirpath) / name
            suffixes = set(path.suffixes)
            if path.suffix in TEXT_EXTS or suffixes.intersection(TEXT_EXTS) or path.name.startswith(".env"):
                yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def git_output(root: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:  # noqa: BLE001 - report, do not fail scan
        return f"unavailable: {exc}"


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="scan repo for README/API/deploy contract cleanup hints")
    parser.add_argument("repo", nargs="?", default=".", help="repository path")
    parser.add_argument("--out", help="write markdown report to this file")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    if not root.exists():
        raise SystemExit(f"repo path does not exist: {root}")

    files = list(iter_files(root))
    fastapi_routes: list[tuple[str, str, str]] = []
    api_strings: list[tuple[str, str]] = []
    env_reads: list[tuple[str, str]] = []
    env_defs: list[tuple[str, str]] = []
    pattern_hits: dict[str, list[tuple[str, int, str]]] = {name: [] for name, _ in STALE_PATTERNS}

    for path in files:
        text = read_text(path)
        rpath = rel(root, path)
        for method, route in FASTAPI_ROUTE_RE.findall(text):
            fastapi_routes.append((method.upper(), route, rpath))
        for api in API_STRING_RE.findall(text):
            api_strings.append((api, rpath))
        for env in ENV_READ_RE.findall(text):
            env_reads.append((env, rpath))
        if path.name.startswith(".env") or "env" in path.parts or path.suffix in {".env", ".example"}:
            for env in ENV_LINE_RE.findall(text):
                env_defs.append((env, rpath))
        for name, regex in STALE_PATTERNS:
            for match in regex.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                line = text.splitlines()[line_no - 1][:180] if text.splitlines() else ""
                pattern_hits[name].append((rpath, line_no, line.strip()))

    lines: list[str] = []
    lines.append("# Repository Contract Scan")
    lines.append("")
    lines.append(f"repo: `{root}`")
    lines.append(f"scanned text files: {len(files)}")
    lines.append("")
    lines.append("## Git baseline")
    lines.append("```text")
    lines.append(git_output(root, ["status", "--short"]))
    lines.append("```")
    lines.append("")

    lines.append("## FastAPI-style routes")
    if fastapi_routes:
        lines.append("| Method | Path | File |")
        lines.append("|---|---|---|")
        for method, route, path in sorted(set(fastapi_routes)):
            lines.append(f"| {method} | `{route}` | `{path}` |")
    else:
        lines.append("No FastAPI decorator routes detected by regex.")
    lines.append("")

    lines.append("## API-like frontend/doc strings")
    if api_strings:
        lines.append("| Path string | File |")
        lines.append("|---|---|")
        for api, path in sorted(set(api_strings))[:300]:
            lines.append(f"| `{api}` | `{path}` |")
        if len(set(api_strings)) > 300:
            lines.append(f"\nTruncated to 300 of {len(set(api_strings))} unique API-like strings.")
    else:
        lines.append("No API-like strings detected.")
    lines.append("")

    lines.append("## Environment variables")
    reads = {env: sorted({path for e, path in env_reads if e == env}) for env, _ in env_reads}
    defs = {env: sorted({path for e, path in env_defs if e == env}) for env, _ in env_defs}
    all_envs = sorted(set(reads) | set(defs))
    if all_envs:
        lines.append("| Variable | Read in | Defined in |")
        lines.append("|---|---|---|")
        for env in all_envs:
            read_in = "<br>".join(f"`{p}`" for p in reads.get(env, [])) or "-"
            defined_in = "<br>".join(f"`{p}`" for p in defs.get(env, [])) or "-"
            lines.append(f"| `{env}` | {read_in} | {defined_in} |")
    else:
        lines.append("No environment variables detected by regex.")
    lines.append("")

    lines.append("## Stale/redundancy pattern hits")
    for name, hits in pattern_hits.items():
        lines.append(f"### {name}")
        if hits:
            lines.append("| File | Line | Text |")
            lines.append("|---|---:|---|")
            for path, line_no, text in hits[:200]:
                safe = text.replace("|", "\\|")
                lines.append(f"| `{path}` | {line_no} | `{safe}` |")
            if len(hits) > 200:
                lines.append(f"\nTruncated to 200 of {len(hits)} hits.")
        else:
            lines.append("No hits.")
        lines.append("")

    report = "\n".join(lines) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
