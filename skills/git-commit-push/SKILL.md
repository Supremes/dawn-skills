---
name: git-commit-push
description: "Streamline git workflow: review changes, generate conventional commits, push to remote. Use when you need to commit and push local changes with a clean, professional commit message. Keywords: git, commit, push, changelog, conventional commit."
license: MIT
metadata:
  version: "1.0.0"
---

# Git Commit & Push Workflow

Automate the process of reviewing local changes, generating a conventional commit message, and pushing to the remote repository.

## Overview

This skill guides you through a structured git workflow:
1. **Review** local changes (`git status` and `git diff`)
2. **Summarize** the changes in human-readable form
3. **Generate** a conventional commit message with scope and body
4. **Execute** `git add`, `git commit`, and `git push` operations
5. **Confirm** the push succeeded

## Prerequisites

- Working git repository with staged or unstaged changes
- Remote repository configured (`origin` by default)
- Local branch tracking the remote (or manual push target specification)

## Workflow

### Step 1: Review Local Changes

Run the following to see what has changed:

```bash
git status
git diff
```

**What to look for:**
- Modified files (unstaged)
- Staged files (ready to commit)
- Untracked files (new files not staged)

**Note:** If you only want a summary, run:
```bash
git status --short
```

### Step 2: Summarize Changes

Read through the `git diff` output and create a concise summary. Identify:
- **Primary scope**: Which component or module is affected? (e.g., `api`, `docs`, `config`)
- **Type of change**: Is it a `feat`, `fix`, `refactor`, `docs`, `chore`, etc.?
- **Key changes**: What is the main intent (e.g., "Add Test Result columns to TC tables", "Fix null pointer in API handler")?

**Example summary:**
```
Files modified: skills/jira-testplan-creator/SKILL.md
Type: feat (enhancement)
Scope: jira-testplan-creator
Change: Added Test Result and Note columns to TC step tables,
        plus overall result tracking per TC
```

### Step 3: Craft Conventional Commit Message

Using the summary from Step 2, construct a conventional commit following this format:

```
<type>(<scope>): <subject>

<body>
```

**Rules:**
- **type**: One of `feat`, `fix`, `refactor`, `docs`, `chore`, `build`, `ci`, `test`, `perf`, `style`
- **scope**: Component affected (optional but recommended, e.g., `jira-testplan-creator`)
- **subject**: Imperative mood, present tense, no period, max 70 characters
  - ✅ "Add Test Result columns to TC tables"
  - ❌ "Added Test Result columns to TC tables"
  - ❌ "Add Test Result columns to TC tables."
- **body** (2-4 sentences): Explain *what* and *why*, not *how*
  - Focus on motivation and context
  - Keep lines under 100 characters

**Example commit:**
```
feat(jira-testplan-creator): Add Test Result and Note columns to TC tables

Add two new columns to every TC step table in the generated test plan:
- Test Result: '⬜ Pass / ⬜ Fail' per step row
- Note: blank cell for tester's free-text remarks

Also add an 'Overall TC-XX Result' summary line after each TC table
for tracking overall pass/fail/skip status.
```

### Step 4: Stage and Commit

Execute the git operations:

```bash
# Stage all changes (or specify individual files)
git add .

# Or stage specific files:
git add <file1> <file2> ...

# Commit with the message from Step 3
git commit -m "feat(scope): subject" -m "Body paragraph with details."

# Or use an editor (avoid for this skill; pre-write the message instead)
git commit
```

**Verification:**
```bash
git log -1  # Should show your new commit
```

### Step 5: Push to Remote

Push the commit to the remote repository:

```bash
# Standard push to origin master/main
git push origin master
# or
git push origin main

# If you're working on a feature branch (recommended):
git push origin <branch-name>

# If origin/branch tracking is set up:
git push
```

**Watch for:**
- ✅ `[master abc123..def456]` → Success; commit pushed
- ❌ `error: failed to push some refs to 'origin'` → Conflict; pull first with `git pull --rebase origin <branch>`
- ❌ Authentication errors → Check SSH key or token setup

**After successful push:**
```bash
git status  # Should say "Your branch is up to date with 'origin/master'"
```

## Common Scenarios

### Scenario 1: Single file change, simple fix

```bash
git diff <file>  # Review
git add <file>
git commit -m "fix(module): Fix typo in error message"
git push origin master
```

### Scenario 2: Multiple files, feature enhancement

```bash
git status  # See all modified files
git diff    # Review all changes
git add .
git commit -m "feat(core): Add caching layer to API" -m "Implement in-memory cache with TTL expiry to reduce database load and improve response time."
git push origin feature/add-caching
```

### Scenario 3: Conflict during push

```bash
# Push fails with "failed to push some refs"
git pull --rebase origin master  # Get latest commits
# Fix any merge conflicts if they appear
git push origin master
```

## Quality Checklist

Before pushing, verify:

- ✅ All intended files are staged (`git status`)
- ✅ Commit message follows conventional format
- ✅ Subject line is ≤70 characters and imperative mood
- ✅ Body (if any) explains *why*, not *how*
- ✅ No sensitive data (keys, passwords) in diff
- ✅ Code review completed (if required by your team)
- ✅ Branch is up to date with remote (`git pull` if needed before final push)

## References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Git Guide](https://github.com/git-tips/tips)

## Related Skills

- **conventional-commit**: Details on commit message format and examples
- **create-pr**: After pushing a feature branch, create a pull request for code review
