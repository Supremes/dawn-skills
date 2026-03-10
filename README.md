# dawn-skills

A collection of custom **skills** and **agents** for the [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli), extending its capabilities with specialized workflows and domain expertise.

## Overview

| Type | Count | Purpose |
|------|-------|---------|
| Skills | 12 | Modular workflow automations |
| Agents | 3 | Domain-specific expert assistants |

---

## 🤖 Agents

Agents are specialized AI personas with deep domain knowledge.

| Agent | Description |
|-------|-------------|
| **daily** | Bilingual conversation partner for daily English practice. Responds in English and corrects grammar in context. |
| **mdm-research** | Researches and summarizes MDM (Mobile Device Management) updates from Apple, Microsoft Intune, and Omnissa for competitive analysis and compliance tracking. |
| **mentor** | Senior Java architect and AI Agent specialist. Guides the journey from advanced Java developer to AI Agent architect with deep technical mentoring. |

---

## 🛠️ Skills

Skills are modular, reusable workflow automations invoked on demand.

### Git & Code Quality

| Skill | Description | Keywords |
|-------|-------------|----------|
| **code-review-expert** | Expert code review detecting SOLID violations, security risks, and architecture issues in current git changes. | `review`, `code review`, `security` |
| **conventional-commit** | Generates conventional commit messages following best-practice standards. | `commit`, `commit message` |
| **git-commit-push** | End-to-end git workflow: reviews changes, generates a conventional commit, and pushes to remote. | `commit and push`, `git push` |
| **create-pr** | Creates pull requests with professional descriptions and structure. | `PR`, `pull request`, `open PR` |

### Jira & Testing

| Skill | Description | Keywords |
|-------|-------------|----------|
| **jira-issue-cli-handler** | Full Jira issue lifecycle via CLI: create, view, search, assign, transition, comment. | `jira`, `issue`, `ticket` |
| **jira-testplan-creator** | Generates comprehensive test plans from Jira issues and GitHub changes, then publishes to Confluence. | `test plan`, `QA`, `test cases` |
| **test-results-reporter** | Summarizes completed test results and posts a formatted report as a Jira comment. | `test results`, `QA report`, `pass/fail` |

### Documentation

| Skill | Description | Keywords |
|-------|-------------|----------|
| **confluence-update** | Updates existing Confluence pages — append sections, replace content, or restructure. | `confluence`, `update docs` |
| **translator** | Translates technical documentation between English and Simplified Chinese, preserving technical terminology. | `translate`, `Chinese`, `English` |
| **local-save-docs** | Saves conversation output or final answers to local files under a fixed root path. | `save`, `export`, `archive` |

### Utilities

| Skill | Description | Keywords |
|-------|-------------|----------|
| **polisher** | Fixes grammar, improves wording, and makes prompts sound natural and concise. | `polish`, `grammar`, `rewrite` |
| **find-skills** | Discovers and installs new agent skills from the open skills ecosystem. | `find skill`, `install skill` |

---

## Structure

```
dawn-skills/
├── agents/             # Custom agent definitions (.agent.md)
│   ├── daily.agent.md
│   ├── mdm-research.agent.md
│   └── mentor.agent.md
└── skills/             # Skill definitions (SKILL.md + optional assets)
    ├── code-review-expert/
    ├── confluence-update/
    ├── conventional-commit/
    ├── create-pr/
    ├── find-skills/
    ├── git-commit-push/
    ├── jira-issue-cli-handler/
    ├── jira-testplan-creator/
    ├── local-save-docs/
    ├── polisher/
    ├── test-results-reporter/
    └── translator/
```
