# Contributing to FactLama Architecture

Thank you for helping improve FactLama. This repository owns system architecture, shared contracts, architecture decisions, security and privacy requirements, and the implementation plan used by the Reliability and Observability repositories.

## Before starting

1. Search existing issues and pull requests to avoid duplicate work.
2. For a substantial architectural change, open an issue describing the problem, proposed behavior, alternatives, and compatibility impact before implementation.
3. Read the documents relevant to the change. Start with `README.md`, then use `EXECUTION_PLAN.md`, `CONTRACTS.md`, the decision register, and the applicable component documentation as needed.
4. Coordinate changes that affect public schemas or both implementation repositories. Update prose contracts, executable schemas, canonical fixtures, and implementation documentation together.

## Get a checkout

If you have write access, clone `https://github.com/Factlama/factlama-architecture.git` and use the branch workflow below. Otherwise, fork the repository on GitHub, replace `YOUR_USERNAME` below, and run:

```bash
git clone https://github.com/YOUR_USERNAME/factlama-architecture.git
cd factlama-architecture
git remote add upstream https://github.com/Factlama/factlama-architecture.git
git fetch upstream
git switch -c feat/short-description upstream/main
```

For a fork, push your feature branch to `origin` (your fork) and open the PR against `Factlama/factlama-architecture:main`. In the GitHub CLI command below, add `--repo Factlama/factlama-architecture`. You can also use GitHub's **Compare & pull request** button instead of installing the CLI.

Keep architecture and implementation checkouts side by side when working across repositories. Clone `https://github.com/Factlama/factlama-architecture.git` beside an implementation checkout so canonical contract tests can find it.

## Create a branch (direct collaborators)

Keep `main` deployable and create a focused branch from the latest upstream version:

```bash
git switch main
git pull --ff-only origin main
git switch -c docs/short-description
```

Use a clear prefix such as `docs/`, `feat/`, `fix/`, or `chore/`.

## Make and verify changes

Keep each pull request focused on one coherent change. Update links and related status sources when appropriate. Before committing, run:

```bash
git diff --check
python contracts/validate.py
```

If the contract validator needs its dependencies, install `contracts/requirements.txt` in a virtual environment first. Documentation-only changes that do not touch contracts still require `git diff --check` and a review of rendered Markdown.

## Commit with sign-off

FactLama uses the [Developer Certificate of Origin](https://developercertificate.org/) sign-off process. By adding a `Signed-off-by` line, you certify that you created the contribution or have the right to submit it under this repository's license.

Configure your real name and email, stage only the intended files, and create a signed-off commit:

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
git add path/to/changed-file
git commit --signoff -m "docs: describe the architecture change"
```

The commit message will contain:

```text
Signed-off-by: Your Name <you@example.com>
```

Do not submit confidential information, employer-owned work without permission, secrets, copied code, model weights, datasets, or other material you do not have the right to contribute.

## Open a pull request

Push the branch and open a pull request against `main`:

```bash
git push -u origin docs/short-description
gh pr create --base main --fill
```

The pull request description should explain:

- the problem and resulting behavior;
- affected contracts, repositories, or compatibility guarantees;
- validation performed;
- security, privacy, tenant-isolation, or migration considerations;
- follow-up work that is intentionally outside the change.

Respond to review comments with additional signed-off commits. Avoid force-pushing a branch while it is under active review unless reviewers have agreed to it.

## Review and merge

Open a draft PR early if you need design feedback. Link the issue and any companion PR in another repository. Include the actual commands and results used for validation; identify skipped checks. Request maintainer review and wait for applicable CI checks and approval before merge. Preserve authorship and sign-off trailers when squashing commits.

Every new contribution commit must carry your DCO sign-off. Read the full [DCO 1.1](https://developercertificate.org/) before signing: it also explains that your contribution and sign-off become public records. A sign-off is a certification of your right to contribute, not a cryptographic signature or copyright transfer. Contributors retain their copyrights; no CLA is currently required.

For your latest local, unpublished commit, a missing sign-off can be added with:

```bash
git commit --amend --no-edit --signoff
```

Only certify work you have the right to submit. Coordinate with maintainers before rewriting a published branch. Sign-offs are reviewed manually unless the repository has a DCO check configured; this guide does not enable GitHub branch protection or a DCO app.

## Licensing

This repository is licensed under the Apache License 2.0. Unless you explicitly state otherwise, every contribution intentionally submitted for inclusion in this repository is provided under Apache 2.0, consistent with section 5 of the license. Third-party code, documentation, datasets, model weights, and generated assets retain their own licenses and must be identified and reviewed before inclusion.


See [LICENSE](LICENSE), [NOTICE](NOTICE), and [LICENSE-HISTORY.md](LICENSE-HISTORY.md) for the license text, attribution, and transition from MIT.
