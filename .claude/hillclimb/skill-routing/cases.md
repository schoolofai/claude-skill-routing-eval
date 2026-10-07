# skill-routing cases

Expected = the skill that should be invoked first, or `none` (no skill should fire).

| id | expected | source | difficulty |
|---|---|---|---|
| c02 | release-notes | real | hard |
| c03 | changelog | real | medium |
| c04 | pr-description | real | hard |
| c05 | weekly-update | real | hard |
| c06 | weekly-update | real | hard |
| c07 | announce | real | medium |
| c08 | none | real | medium |
| c09 | announce | synthetic | easy |
| c10 | announce | synthetic | easy |
| c11 | announce | synthetic | medium |
| c12 | announce | synthetic | hard |
| c13 | release-notes | synthetic | easy |
| c14 | release-notes | synthetic | medium |
| c15 | release-notes | synthetic | medium |
| c16 | release-notes | synthetic | hard |
| c17 | changelog | synthetic | easy |
| c18 | changelog | synthetic | medium |
| c19 | changelog | synthetic | medium |
| c20 | changelog | synthetic | hard |
| c21 | pr-description | synthetic | easy |
| c22 | pr-description | synthetic | easy |
| c23 | pr-description | synthetic | medium |
| c24 | pr-description | synthetic | hard |
| c25 | weekly-update | synthetic | easy |
| c26 | weekly-update | synthetic | medium |
| c27 | weekly-update | synthetic | hard |
| c28 | weekly-update | synthetic | hard |
| c29 | none | synthetic | medium |
| c30 | none | synthetic | easy |
| c31 | none | synthetic | easy |
| c32 | none | synthetic | easy |
| c33 | none | synthetic | easy |
| c34 | none | synthetic | medium |
| c35 | none | synthetic | medium |
| c36 | none | synthetic | medium |
| c37 | none | synthetic | easy |
| c38 | none | synthetic | medium |
| c39 | none | synthetic | medium |
| c40 | none | synthetic | hard |
| c41 | none | synthetic | easy |
| c42 | none | synthetic | hard |

## c02 → release-notes
```
Support keeps asking what changed in the last version. Put together a summary they can send to customers.
```

## c03 → changelog
```
I just fixed the retry bug in PR 88, log it so it shows up next release.
```

## c04 → pr-description
```
Summarize what this branch changes so the reviewer knows where to look.
```

## c05 → weekly-update
```
What did we merge this week? Just a quick list for standup.
```

## c06 → weekly-update
```
My manager wants to know what shipped since the last release, including the CI work.
```

## c07 → announce
```
Write something for our newsletter about 1.4 being out.
```

## c08 → none
```
Bump the version to 1.4.0 and tag it.
```

## c09 → announce
```
Draft a LinkedIn post for the 1.4 launch.
```

## c10 → announce
```
Write the blog intro for our 1.4 release, something upbeat.
```

## c11 → announce
```
Need a tweet that gets people excited about the new version.
```

## c12 → announce
```
Marketing wants a short blurb about what's new, for the newsletter.
```

## c13 → release-notes
```
Write the release notes for 1.4.0.
```

## c14 → release-notes
```
Draft what's new for customers, grouped into new, improved and fixed.
```

## c15 → release-notes
```
We ship tomorrow. What should we tell users changed since v1.3.0?
```

## c16 → release-notes
```
Customers need to know about the breaking changes in this version and what they have to do about them.
```

## c17 → changelog
```
Add an entry to the changelog for my branch.
```

## c18 → changelog
```
Record this under Unreleased: queue.pop() no longer raises on an empty queue. PR 91.
```

## c19 → changelog
```
We removed the legacy flush() API, note that in CHANGELOG.md.
```

## c20 → changelog
```
One-liner for the dev-facing log of this change, Added/Changed/Fixed style.
```

## c21 → pr-description
```
Write the PR body for this branch.
```

## c22 → pr-description
```
Draft the pull request description, include how it was tested.
```

## c23 → pr-description
```
Reviewers keep missing the retry change. Write up what changed and where to start looking.
```

## c24 → pr-description
```
I'm about to open a PR from these commits, can you write the text for it?
```

## c25 → weekly-update
```
Weekly update for the team please.
```

## c26 → weekly-update
```
Summarize what we worked on in the last 7 days, grouped by person.
```

## c27 → weekly-update
```
What did the team ship and refactor lately? It's for our internal sync.
```

## c28 → weekly-update
```
Status report for my manager on what landed since Monday.
```

## c29 → none
```
Cut a git tag v1.4.1 and push it.
```

## c30 → none
```
Fix the bug where queue.pop() raises on an empty queue.
```

## c31 → none
```
Add type hints to src/queue.py.
```

## c32 → none
```
What does the Queue class in src/queue.py do?
```

## c33 → none
```
Run the tests and tell me what fails.
```

## c34 → none
```
Merge PR 88 into main.
```

## c35 → none
```
Publish the package to PyPI.
```

## c36 → none
```
Pin claude-agent-sdk to the latest version in requirements.txt.
```

## c37 → none
```
Write a short poem about queues.
```

## c38 → none
```
Review my PR for bugs and style problems.
```

## c39 → none
```
Delete the merged branches and clean up the repo.
```

## c40 → none
```
What makes a good changelog, in general? I'm writing a blog post about it.
```

## c41 → none
```
Translate the README into Spanish.
```

## c42 → none
```
Bump the version to 1.5.0 and update the version string in the README.
```

## c43 → none  (user-written look-alike)
```
Show me last week's commits.
```

## c44 → none  (user-written look-alike)
```
What's in this diff? I just want to understand it before I touch anything.
```

## c45 → none  (user-written look-alike)
```
List the release tags we've published so far.
```

## c46 → none  (user-written look-alike)
```
When did the retry fix land? Find the commit.
```

## c47 → none  (user-written look-alike)
```
Fix the typo in the 1.3.0 heading of CHANGELOG.md.
```

## c48 → none  (user-written look-alike)
```
Why did the sync API break after the last release? Dig through the history.
```

## c49 → none  (user-written look-alike)
```
Write a docstring for Queue.pop.
```

## c50 → none  (user-written look-alike)
```
Who merged the most PRs this month?
```

## c51 → none  (user-written look-alike)
```
Give me a git alias that prints merges since the last tag.
```

## c52 → none  (user-written look-alike)
```
Did anything change in src/queue.py since v1.3.0?
```

## c53 → pr-description  (user-written look-alike)
```
Before Dana reviews, give her the lay of the land for this branch.
```

## c54 → release-notes  (user-written look-alike)
```
Users upgrading from 1.3 need to know what's different. Write that up.
```

## c55 → release-notes  (user-written, between two skills)
```
What's new for users in 1.4? List every fix so they can plan the upgrade.
```

## c56 → announce  (user-written, between two skills)
```
Give me three upbeat sentences about 1.4 for the homepage banner.
```

## c57 → weekly-update  (user-written, between two skills)
```
Summarize everything since the last release for the eng team's Friday sync.
```

## c58 → release-notes  (user-written, between two skills)
```
Summarize everything since the last release for customers, grouped into new and fixed.
```

## c59 → changelog  (user-written, between two skills)
```
Log the retry fix from this branch for other developers, one line with the PR number.
```

## c60 → announce  (user-written, between two skills)
```
The 1.4 notes are done. Now write the LinkedIn post that links to them.
```

## c61 → pr-description  (user-written, between two skills)
```
Write up the breaking change in this branch for the reviewer, not for users.
```

## c62 → changelog  (user-written, between two skills)
```
Add the removal of flush() to the unreleased section. The release notes come later.
```

## c63 → weekly-update  (user-written, between two skills)
```
Tell the team what we released on Tuesday and what else got done this week.
```

## c64 → pr-description  (user-written, between two skills)
```
Explain this branch's changes so Sam can approve the PR. Don't touch the changelog.
```
