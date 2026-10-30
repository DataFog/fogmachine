# fogmachine engineering rules

Keep shared environment mechanics here and product semantics in their own repositories.
Read docs/architecture.md before changing the toolchain contract.
Changes to command dispatch, failure handling, or pin validation require positive and negative tests.
Run `python3 -m unittest discover -s tests` and `actionlint` before submitting workflow changes.
User-facing changes require an Unreleased changelog entry; internal-only PRs require
both `no-changelog` and `Changelog exemption: <reason>` in the body.
Keep audit output free of secrets. Publish images only after the pilot matrix succeeds.

Use `fogmachine` in lowercase in all user-facing prose and labels.
