#!/usr/bin/env python3
"""Fail if common secrets or personal/local identifiers are found."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
}

TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml",
    ".sql", ".env", ".example", ".dockerignore", ".gitignore",
}

PATTERNS = {
    "Supabase JWT/service key": re.compile(r"eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{10,}"),
    "OpenAI/OpenRouter-like secret": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "Bearer token": re.compile(r"Bearer\s+[A-Za-z0-9._~-]{16,}", re.I),
    "macOS user path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "Linux home user path": re.compile(r"/home/(?!oai/)[A-Za-z0-9._-]+/"),
    "Windows user path": re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\\]+\\\\"),
    "n8n instanceId": re.compile(r'"instanceId"\s*:'),
    "n8n credentials block": re.compile(r'"credentials"\s*:'),
}


findings = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if path.resolve() == Path(__file__).resolve():
        continue

    if any(part in SKIP_DIRS for part in path.parts):
        continue

    if path.name == "secrets.toml":
        findings.append((path, "real Streamlit secrets file"))
        continue

    # Skip binary assets.
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
        "Dockerfile", ".gitignore", ".dockerignore"
    }:
        continue

    try:
        text = path.read_text(errors="ignore")
    except Exception:
        continue

    for label, pattern in PATTERNS.items():
        if pattern.search(text):
            # "credentials" is expected in documentation/scripts explaining sanitization.
            if label in {"n8n credentials block", "n8n instanceId"} and path.parts[-2:] in {
                ("scripts", "check_public_repo.py"),
                ("scripts", "sanitize_n8n_export.py"),
            }:
                continue
            findings.append((path, label))

if findings:
    print("Potential public-repository issues found:")
    for path, label in findings:
        print(f"- {path.relative_to(ROOT)}: {label}")
    raise SystemExit(1)

print("Public-repository scan passed: no obvious secrets/local identifiers found.")
