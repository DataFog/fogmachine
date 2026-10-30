# Contributing

Follow AGENTS.md. Run `python3 -m unittest discover -s tests`,
`python3 scripts/test-changelog.py`, and `actionlint`.

User-facing changes require a bullet under `## [Unreleased]` in CHANGELOG.md.
Internal-only exemptions require both the no-changelog PR label and a nonempty
`Changelog exemption: <reason>` body line. The policy checks the full committed PR
against its actual target, including stacked PRs; headings and historical edits do
not qualify. Reviewers confirm accuracy. Environment changes require both pilots
before image publication. Local builds cannot substitute for hosted/native evidence.
