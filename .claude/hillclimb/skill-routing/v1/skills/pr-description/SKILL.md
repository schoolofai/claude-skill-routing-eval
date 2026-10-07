---
name: pr-description
description: "Writes the pull request body for the current branch (what changed, why, testing, where the reviewer should look first), including requests to summarize a branch for a reviewer. Use this first, before running git commands; it reads the diff itself. Not for reviewing a PR, merging, or code changes."
---

# Pull request description

Write the description for the current branch's pull request, for the reviewer: what changed, why,
how it was tested, and where to look first. Read `git diff main...HEAD`. Output markdown for the PR body.
