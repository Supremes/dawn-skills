---
name: jira-issue-cli-handler
description: 'Handle Jira issue workflows with Atlassian CLI: auth, create, view, search, assign, update, comment, and transition. Use when triaging or executing issue operations from terminal.'
argument-hint: 'What Jira operation do you need (create, update, transition, assign, comment, search, view)?'
---

# Jira Issue CLI Handler

Use Atlassian CLI (ACLI) to run reliable Jira issue workflows from the terminal.

## When to Use
- You need to create or update Jira issues quickly from CLI.
- You need repeatable issue triage workflows (search, assign, transition, comment).
- You need machine-readable output using `--json` for automation.

## Scope And Terminology
- ACLI command group uses `workitem` terminology:
  - `acli jira workitem ...`
- In this skill, "issue" and "work item" are treated as equivalent Jira entities.

## Prerequisites
1. ACLI is installed and available in PATH.
2. You can authenticate to Jira Cloud.
3. You know project key, issue type, and target issue key(s) where applicable.

## Step-by-Step Workflow

### Step 1: Verify CLI and Auth
Run:

```bash
acli --help
acli jira auth status
```

If not authenticated:

```bash
acli jira auth login
```

Completion check:
- `acli jira auth status` shows an authenticated account for the intended Jira site.

### Step 2: Choose Operation Path
Pick one path based on intent:
- Create new issue: Step 3A
- Retrieve issue details: Step 3B
- Find issues with JQL/filter: Step 3C
- Update fields: Step 3D
- Assign or unassign: Step 3E
- Add comment: Step 3F
- Transition status: Step 3G

### Step 3A: Create Issue
Minimal create:

```bash
acli jira workitem create --summary "New Task" --project "TEAM" --type "Task" --json
```

Richer create example:

```bash
acli jira workitem create \
  --summary "Fix login timeout handling" \
  --description "Handle timeout response and show retry guidance" \
  --project "TEAM" \
  --type "Bug" \
  --assignee "@me" \
  --label "backend,timeout" \
  --json
```

Decision points:
- Use `--editor` when the description is long.
- Use `--from-json` for repeatable scripted creation.

Completion check:
- Response includes created key (for example `TEAM-123`).

### Step 3B: View Issue
Run:

```bash
acli jira workitem view TEAM-123 --fields "key,summary,status,assignee,description" --json
```

Decision points:
- Use `--fields` for focused output.
- Use `--web` for browser inspection.

Completion check:
- Returned issue key matches requested key and includes expected fields.

### Step 3C: Search Issues
Run:

```bash
acli jira workitem search --jql "project = TEAM AND status != Done ORDER BY updated DESC" --limit 50 --json
```

Alternative with filter:

```bash
acli jira workitem search --filter 10001 --json
```

Decision points:
- Use `--paginate` for complete result retrieval.
- Use `--count` for quick triage metrics.

Completion check:
- Output contains expected issue set and count.

### Step 3D: Update Issue Fields
Update by key:

```bash
acli jira workitem edit --key "TEAM-123" --summary "Updated summary" --description "Updated details" --json
```

Bulk update by JQL:

```bash
acli jira workitem edit --jql "project = TEAM AND labels = stale" --labels "refined" --yes --json
```

Decision points:
- Use `--yes` for non-interactive scripts.
- Use `--from-json` for complex field sets.

Completion check:
- Follow with `acli jira workitem view TEAM-123 --json` and verify field changes.

### Step 3E: Assign Or Unassign
Assign:

```bash
acli jira workitem assign --key "TEAM-123" --assignee "@me" --json
```

Unassign:

```bash
acli jira workitem assign --key "TEAM-123" --remove-assignee --json
```

Completion check:
- Issue assignee field reflects intended value.

### Step 3F: Add Comment
Run:

```bash
acli jira workitem comment create --key "TEAM-123" --body "Investigated root cause. Proposed fix in PR #456." --json
```

Decision points:
- Use `--body-file` for long updates.
- Use `--edit-last` when revising your previous comment.

Completion check:
- Comment appears in issue activity.

### Step 3G: Transition Status
Run:

```bash
acli jira workitem transition --key "TEAM-123" --status "In Progress" --json
```

Decision points:
- Use exact status names available in workflow.
- For batch transitions, use `--jql` with care and add `--yes` only after previewing target issues.

Completion check:
- `status` field is updated to the requested state.

## Quality Criteria
- Commands are scoped correctly (`--key`, `--jql`, or `--filter`) and not overly broad.
- JSON output is used when results need to be parsed or audited.
- Every write action (create/edit/assign/comment/transition) is followed by a verification read (`view` or `search`).
- Bulk operations are previewed first with a read-only search.

## Safe Execution Pattern
1. Preview target issues with `search`.
2. Execute one issue first.
3. Verify output and resulting state.
4. Scale to batch operations.

## Troubleshooting
- Auth errors: run `acli jira auth status` then `acli jira auth login`.
- Permission errors: verify project role and issue security level.
- Status transition fails: check exact status value and workflow transition availability.
- Field update fails: confirm field is editable for issue type/screen configuration.

## Compatibility Note
Atlassian CLI reference currently documents `acli jira workitem ...` commands. If your local environment exposes older aliases such as `issue`, prefer `workitem` for forward compatibility.
