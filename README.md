# fogmachine

Shared development environments for DataFog Core and MCP. Initial pilot; see CI for qualification status.

The shared image provides Ubuntu 24.04, Python 3.12, Node 24, Rust, uv, maturin,
wasm-bindgen, and Playwright Chromium. `toolchains.json` owns tool requirements;
product lockfiles continue to own project dependencies. Node is a major-version
contract, Python a minor-version contract; exact installed versions are identified
by the published image digest. Rebuilding may update OS packages and Node patches.

Inside a pilot checkout with `.fogmachine.json`, run:

```sh
./dev setup
./dev doctor
./dev check
```

`dev` delegates to `/opt/fogmachine/dev` in the container. Setup installs frozen
repo dependencies and builds artifacts. Doctor checks tools and product pins.
Check runs the existing product suites. Failures return nonzero; reports and logs
remain under `.fogmachine-runs/` (ignored by Git). Build/setup is explicit, not an
implicit side effect of doctor. See [architecture](docs/architecture.md) and
[pilot adoption](docs/pilots.md).

Development images are published to `ghcr.io/datafog/fogmachine` only after Core
and MCP pass on the candidate image. Consumers pin the resulting digest; no
consumer should track `latest`. Package visibility is managed separately in GHCR. If the package is private, grant
consuming repos access and authenticate developers with read:packages. No credentials
are included in images. ARM64 qualification and native macOS/Windows lanes remain
separate from this initial Linux AMD64 pilot.
