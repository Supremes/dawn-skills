---
name: local-save-docs
description: "Save conversation content or final answers to local files under a fixed root path. Use when user asks to save, archive, export, or persist chat output locally."
argument-hint: "What content should be saved (full conversation, summary, or final answer), and what document type?"
---

# Local Save Docs

Save requested content to local files with a fixed root directory:
- `/Users/junkangd/officeDocuments/officeDocs`

## When To Use
- User asks to save conversation content locally.
- User asks to save your answer/output to a local file.
- User asks to archive summaries, reports, plans, or checklists on disk.

## Hard Rules
1. Always save under this root path only:
   - `/Users/junkangd/officeDocuments/officeDocs`
2. You may create subdirectories under this root to separate document types.
3. Never save outside the root path unless user explicitly overrides and confirms.
4. Use Markdown (`.md`) by default unless user requests another format.

## Workflow

### Step 1: Confirm Save Intent And Scope
Decide content scope from user request:
- Full conversation transcript
- Structured summary
- Final answer only
- Specific section(s)

If unclear, ask one concise clarification question.

### Step 2: Choose Document Type Folder
Map content to a subdirectory under the fixed root:
- `conversation-notes/`: full chat notes or transcripts
- `answer-archives/`: final answers and one-off outputs
- `test-plans/`: QA test plans
- `workflows/`: procedures, checklists, runbooks
- `reports/`: analysis reports and summaries

If no clear type, use `answer-archives/`.

### Step 3: Build File Name
Use a stable and readable naming pattern:
- `<topic>-<YYYY-MM-DD>.md`

Rules:
- Lowercase words
- Replace spaces with `-`
- Remove special characters not suitable for filenames
- Keep filename concise but specific

Example:
- `cxm-121434-test-plan-2026-03-10.md`

### Step 4: Create Directory And Save File
1. Ensure target directory exists under:
   - `/Users/junkangd/officeDocuments/officeDocs`
2. Write document content to target file.
3. Preserve user language (Chinese/English/bilingual) as requested.

### Step 5: Verify Save Result
After writing file, validate:
- File exists at expected path
- Content is non-empty and matches requested scope
- Path is under fixed root directory

Return confirmation with exact path.

## Decision Points
- If user asks for "save this conversation": prefer `conversation-notes/`.
- If user asks for "save your answer": prefer `answer-archives/`.
- If content is test-related: prefer `test-plans/`.
- If user gives a filename/path fragment: keep it, but normalize under fixed root.

## Quality Checklist
- Saved path starts with `/Users/junkangd/officeDocuments/officeDocs`
- Correct subdirectory selected for content type
- Filename is deterministic and readable
- Saved content matches user request (no missing sections)
- Confirmation includes full local path

## Example Prompts
- "把这段对话保存到本地"
- "请把你的最终回答保存成 markdown"
- "将这个测试计划归档到本地文档目录"
- "保存到 officeDocs 下，并按 report 分类"
