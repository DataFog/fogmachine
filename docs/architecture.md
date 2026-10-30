# Environment contract

fogmachine owns the shared image, tool installation, pilot adapters, and environment
qualification. Product repositories own public behavior, tests, lockfiles, and their
supported runtime/platform matrices. An environment update must not rewrite those
contracts to get a green build.

The initial common toolchain is derived from Core's existing Ubuntu development
image plus MCP's uv requirements. No model weights are downloaded on container
creation. Model qualification remains an explicit Core task. A shared Linux image
does not qualify Apple frameworks, Windows bindings, or FogVault's Xcode/mobile work.

Each repo keeps a small devcontainer config pointing at a tested image digest, a
`.fogmachine.json` profile, and a `dev` forwarding script. Version checks reject
incompatible product pins. Repo-local dependency directories must not be shared
with the host or other worktrees; container volumes isolate `.venv`, `node_modules`,
and Rust build outputs. Only disposable download caches may be shared.

CI builds one candidate and runs Core and MCP separately using that exact image.
Pilot source commits are explicit inputs in workspace/pilots.json. Changing them is
reviewable. Publication occurs after both pass. Adoption is by product PRs updating
the digest, which allows independent rollout and rollback. Private GHCR access and
required merge checks must be configured separately and verified on GitHub.

The pilot tests each repo against its own declared dependencies. It does not install
a candidate Core wheel into MCP: MCP currently constrains Core to <0.5. Cross-repo
candidate compatibility is future integration work, not an environment guarantee.

Verification reports identify the source SHA, dirty diff/status, image identifier,
command exit codes, and logs. They may contain source diffs: use synthetic fixtures
and never place secrets in tracked files. CI uploads evidence after failures.
