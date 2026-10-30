# Core and MCP pilot

The candidate workflow builds and checks the commits in `workspace/pilots.json`.
It uses frozen npm/uv dependencies and Core's own verification CLI. It does not
modify those checkouts' source contracts or invoke publishing.

For local image qualification:

```sh
docker build -t fogmachine:local .
# Run from a product checkout, using a disposable clone rather than host artifacts:
docker run --rm -e FOGMACHINE_IMAGE=fogmachine:local -v "$PWD:/workspace" fogmachine:local /opt/fogmachine/dev setup --profile core
```

The single command above demonstrates setup only. Use `docker create`/`docker exec`
(or `scripts/pilot.sh`) to retain the disposable container through setup, doctor, and
check. Use `mcp` for MCP. Do not mount host-built dependency directories.
The hosted workflow demonstrates this without relying on a machine's installed tools.

After successful image publication, take the digest from the publish job and use
`ghcr.io/datafog/fogmachine@sha256:...` in each pilot devcontainer. Grant private
package read access to the product repos in GHCR package settings. Local developers
must authenticate with a credential that can read the private package. Hosted
cross-repo jobs require package access in addition to packages:read permission.

Consumer pilot branches are proposed independently; do not merge a placeholder
image reference. Existing native release and supported-Python-version CI stay in place.
Later adoption: FogVault browser requirements, ARM64 image qualification, local Core
wheel/tarball consumer integration, and a combined checkout workspace.
