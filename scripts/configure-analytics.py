#!/usr/bin/env python3
"""Prepare public analytics configuration from the build environment."""
import json
import os
from pathlib import Path
import re
import sys

token = os.environ.get("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "").strip()
if token and not re.fullmatch(r"[0-9a-fA-F]{32}", token):
    sys.exit("CLOUDFLARE_WEB_ANALYTICS_TOKEN must be a 32-character hexadecimal site token")
output = Path(sys.argv[1])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"token": token}) + "\n", encoding="utf-8")
print("Cloudflare Web Analytics: " + ("configured" if token else "disabled (no site token)"))
