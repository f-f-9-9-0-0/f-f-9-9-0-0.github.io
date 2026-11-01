#!/usr/bin/env python3
"""Verify the pinned presentation files have not diverged from their snapshot."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / 'scripts/portfolio-template.lock.json').read_text())
for name, expected in manifest['files'].items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit('Presentation snapshot changed: ' + name)
print(f"Presentation snapshot verified: {len(manifest['files'])} files")
