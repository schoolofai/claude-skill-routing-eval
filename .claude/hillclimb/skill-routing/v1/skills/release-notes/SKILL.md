---
name: release-notes
description: "Writes customer-facing release notes for a version: what users should be told changed since a previous tag or release, including breaking changes and upgrade actions. Use this first, before running git commands to find tags or commits; it does that itself. Not for tweets, changelog entries, or internal reports."
---

# Release notes

Write the customer-facing release notes for a new version of this project.

## Steps

1. Find the previous release tag: `git describe --tags --abbrev=0`.
2. List what was merged since then: `git log <tag>..HEAD --merges --oneline`.
3. Sort each change into **New**, **Improved**, **Fixed** or **Breaking changes**. Drop internal-only
   changes (CI, refactors, dependency bumps with no user impact).
4. Write one plain-English line per change, from the user's point of view. No PR numbers, no author names.
5. Put breaking changes first, each with a one-line "what you need to do".
6. Save the result to `docs/releases/vX.Y.Z.md` and show it to the user.
