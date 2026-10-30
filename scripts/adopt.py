#!/usr/bin/env python3
"""Write a thin pilot configuration referencing a qualified immutable image."""
import argparse
import json
from pathlib import Path
import re


def configuration(profile, image):
    if profile not in ("core", "mcp"):
        raise ValueError("profile must be core or mcp")
    if not re.fullmatch(r"ghcr\.io/datafog/fogmachine@sha256:[0-9a-f]{64}", image):
        raise ValueError("a qualified ghcr.io/datafog/fogmachine digest is required")
    directories = [".venv"] if profile == "mcp" else ["target", "bindings/node/node_modules", "bindings/wasm/node_modules"]
    config = {"name": "DataFog " + profile.upper() + " / FogMachine",
              "image": image, "remoteUser": "ubuntu", "workspaceFolder": "/workspace",
              "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind",
              "containerEnv": {"FOGMACHINE_IMAGE": image},
              "mounts": [{"source": "fogmachine-${devcontainerId}-" + directory.replace("/", "-"),
                          "target": "/workspace/" + directory, "type": "volume"} for directory in directories],
              "postCreateCommand": "./dev setup"}
    files = {".devcontainer/devcontainer.json": json.dumps(config, indent=2) + "\n",
             ".fogmachine.json": json.dumps({"profile": profile}, indent=2) + "\n",
             "dev": '#!/usr/bin/env bash\nset -euo pipefail\nif [[ ! -x /opt/fogmachine/dev ]]; then\n  echo "Open this checkout in its FogMachine devcontainer first." >&2\n  exit 1\nfi\nexec /opt/fogmachine/dev "$@"\n'}
    if profile == "core":
        files[".cursor/Dockerfile"] = "FROM " + image + "\n"
        files[".cursor/environment.json"] = json.dumps({"name": "DataFog Core / FogMachine", "build": {"dockerfile": "Dockerfile", "context": ".."}, "user": "ubuntu", "install": "./dev setup"}, indent=2) + "\n"
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["core", "mcp"], required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    files = configuration(args.profile, args.image)
    expected = "Cargo.toml" if args.profile == "core" else "pyproject.toml"
    if not (args.repo / expected).is_file():
        parser.error("target is missing " + expected)
    for name, content in files.items():
        path = args.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (args.repo / "dev").chmod(0o755)
    ignore = args.repo / ".gitignore"
    previous = ignore.read_text() if ignore.exists() else ""
    if ".fogmachine-runs/" not in previous.splitlines():
        ignore.write_text(previous.rstrip() + "\n.fogmachine-runs/\n")


if __name__ == "__main__":
    main()
