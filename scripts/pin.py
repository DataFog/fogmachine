#!/usr/bin/env python3
"""Read the environment's declared tool requirements."""
import json
from pathlib import Path
import sys

if len(sys.argv) != 2:
    sys.exit("usage: pin.py TOOL")
try:
    print(json.loads((Path(__file__).resolve().parents[1] / "toolchains.json").read_text())[sys.argv[1]])
except (OSError, ValueError, KeyError) as error:
    sys.exit(str(error))
