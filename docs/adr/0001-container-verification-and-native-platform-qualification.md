# ADR 0001: Container verification and native platform qualification

- Date: 2026-10-31
- Status: Proposed; acceptance is by merging this ADR. Implementation is tracked separately.

## Context

FogMachine standardizes shared development environments. Product repositories own
their behavior, tests, dependency locks and supported runtime/platform matrices.
The initial image pilot qualifies Linux AMD64 against Core and MCP; that evidence
does not qualify native macOS, Windows or ARM64 behavior.

Kanbun's Electron work makes the boundary concrete. Its full Linux devcontainer
verifier compiles JavaScript consumed by native Mac and Windows packaging jobs.
The packaging jobs passed, but a downloaded ARM64 Mac development bundle failed
`codesign --verify --deep --strict` and was locally ad-hoc signed before launch.
Producing an installer and qualifying the installed application are separate results.

We need a shared contract for these results without changing product pins or
accumulating inconsistent repository-specific exceptions.

## Decision

### Verification stays in the declared environment

Use a qualified image pinned by digest for container-compatible setup, compilation
and verification. Record its identity and the exact source revision. Consumers
select a versioned profile and immutable workflow reference. A change to the image,
toolchain contract or profile requires qualification and a reviewable consumer upgrade.

Product repositories declare their supported OS versions, CPU architectures,
verification commands and distributable inputs. FogMachine validates and executes
that declaration. It does not expand product support or relax tests to obtain a pass.

### Native work is an explicit environment class

Declare native packaging, signing and platform qualification as named lanes with
explicit permissions, runner image/version and toolchain versions. A successful
container verifier gates those lanes. Frozen installation of packaging dependencies
is allowed in an isolated native workspace.

Reuse verified platform-independent output, such as JavaScript, through an artifact
handoff. Native dependencies and platform-specific binaries must be built for their
actual OS/CPU in the declared lane; a Linux build is not substituted for native output.
Record any target-specific compilation and verification in that lane's evidence.

Container, host, native-runner and worktree dependency/build directories remain
separate. Only disposable download caches may be shared. Document these environment
classes in shared policy and consumer instructions so the exception has one meaning.

### The handoff carries evidence

Each run produces a manifest identifying source SHA and clean/dirty state, the image
digest or native runner image identity, toolchain versions, OS/CPU target, commands,
results, and input/output artifact identities and checksums. Native consumers check
the expected source, target and checksums before using inputs. Missing, mismatched,
tampered or unsuccessfully verified inputs fail the gate. Release candidates must
come from clean, reviewed source.

Retain manifests and useful logs on failure, with secrets excluded. Record skipped
or unavailable lanes as unqualified. Packaging, runtime qualification and release
approval remain distinguishable results.

### Platform qualification tests the delivered artifact

For each claimed OS/CPU support lane, inspect package metadata and signatures,
install the produced artifact in an isolated environment, launch it, and execute
the product's native smoke checks. Record the actual tested OS version and CPU;
cross-packaging on one runner does not establish runtime support for every target
or minimum OS version. Products define the minimum-version test coverage they require.

Development jobs may apply an explicit, documented ad-hoc signature. Record that
step and qualify the resulting development artifact. A local signing repair does
not turn the original downloaded artifact into qualified evidence. Public Mac
releases need Developer ID/notarization checks; Windows releases need the declared
trusted-signing checks. Development signing does not satisfy those release gates.

### Release privileges stay separate

PR verification and development packaging have no release-signing credentials.
Signing, notarization and publication use protected release jobs with explicit
authorization and narrowly scoped credentials. They consume verified inputs and
record provenance for the signed outputs. Verification does not publish a product
release as a side effect. Existing Core/MCP gates still control shared-image publication.

### Adoption resolves compatibility explicitly

Adoption must preserve each product's verification and rollback path. At this
decision, Kanbun pins Node 22 and Playwright 1.64.1; FogMachine declares Node 24 and
Playwright 1.62.1. Either qualify a reviewed Kanbun toolchain migration or provide a
versioned compatible profile/image. Do not silently substitute tools, install a
placeholder digest or infer compatibility from successful image construction.

## Consequences

Consumers share verification and platform-workflow mechanics while retaining
product semantics. Evidence identifies exactly which environment and target passed.
Native runner capacity, native tests and release credentials remain real operating
requirements; a devcontainer does not remove them.

We reject both a universal Linux-only support claim and unrestricted host builds.
We also reject treating successful cross-packaging as runtime qualification. Native
work has an explicit contract, isolated state and target-specific evidence.

## Implementation and adoption

This ADR does not implement workflows, expand the initial image's qualification,
migrate a consumer or provision credentials.

- [Shared workflow implementation](https://github.com/DataFog/fogmachine/issues/2)
- [Kanbun adoption](https://github.com/sidmohan0/kanbun/issues/32), dependent on the shared implementation
- [Kanbun desktop reference](https://github.com/sidmohan0/kanbun/pull/30)
- [Environment contract](../architecture.md)
