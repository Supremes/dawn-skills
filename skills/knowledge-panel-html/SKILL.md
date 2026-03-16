---
name: knowledge-panel-html
description: "Use when creating or refactoring long-form HTML knowledge pages, technical explainer pages, protocol overviews, study notes, visual reference pages, or when the user asks to parse an existing HTML page style and generate a reusable template. Keywords: HTML 页面风格分析, 可复用模板, agent skill, 技术长文, 知识展板, 专题页, GitHub Primer 风格页面, knowledge panel, docs page."
---

# Knowledge Panel HTML

Converts a structured Markdown document into a self-contained GitHub Primer–styled HTML page (two-column layout, sticky sidebar, dark code blocks). Template: `templates/github-style-panel.html`.

---

## Input Contract

Source Markdown **must** follow this structure for deterministic output:

```
# Title
> One-line description (used in repo-header and About box)

## Section Name   ← maps to one <section class="gh-section">
...content...

## Next Section
...
```

Optional per-section frontmatter override (YAML comment at H2 line):
```markdown
## Section Name <!-- type: cards|steps|table|code|alert -->
```
When `type` is declared, skip the decision table below and use that component directly.

---

## Component Decision Rules

Apply the **first matching rule** for each `##` section. Do not deviate.

| Section content pattern | Required component |
|---|---|
| H2 with `<!-- type: X -->` override | Use X directly |
| ≥3 H3 blocks, each 2–5 lines of prose | `.gh-card-grid` |
| Ordered list with clear sequential steps | `.gh-step-list` |
| Markdown table or ≥2 columns of comparison | `.gh-table-wrap > .gh-table` |
| Fenced code block(s) as primary content | `.gh-code-block` |
| `> [!NOTE]` / `> [!TIP]` / `> [!WARNING]` / `> [!IMPORTANT]` / `> [!CAUTION]` | `.gh-alert --note/tip/warning/important/caution` |
| `> [!INFO]` / `> [!QUOTE]` / `> [!EXAMPLE]` | `.gh-alert--note` |
| `> [!SUCCESS]` | `.gh-alert--tip` |
| `> [!DANGER]` | `.gh-alert--caution` |
| `> [!ABSTRACT]` | `.gh-alert--important` |
| `<details>` or Q&A / expandable content | `.gh-details` |
| Diff / before-after code comparison | `.gh-diff` |
| Final section titled "总结" / "Summary" / "TL;DR" | `.summary-panel` |
| Anything else | prose `<p>` inside `.gh-section`, no extra wrapper |

---

## Required Page Structure

```
<header class="repo-header">          ← H1 title + > description
<div class="gh-layout">
  <main class="gh-content">
    <section class="gh-section" id="...">   ← one per H2
      [component from Decision Rules]
    </section>
    ...
    <div class="summary-panel">...</div>    ← last section only
  </main>
  <aside class="gh-sidebar">
    <div class="toc-box">...</div>          ← TOC first
    <div class="about-box">...</div>        ← About second
  </aside>
</div>
```

Minimal JS: scroll-spy TOC active link + copy-code button. No other scripts.

---

## CSS Policy

**Do NOT regenerate CSS.** Copy the exact `<style>` block verbatim from `templates/github-style-panel.html`. The CSS is frozen.

- Use only `--gh-*` variables for color; do not add new variables.
- Do not invent class names. If a content need cannot be met by an existing class, adapt the closest available component.
- Do not add inline `style=""` attributes except for `background-color` on syntax-highlighted `<span>` tokens.

---

## Image Handling

Every `![alt](src)` must be preserved. Wrap in `.gh-figure`:

```html
<figure class="gh-figure">
  <img src="URL_OR_RELATIVE_PATH" alt="alt text" />
  <figcaption class="gh-figure__caption">alt text</figcaption>
</figure>
```

- Remote `http(s)://` → embed directly.  
- Local path → use as-is (works when HTML is served from same directory).  
- Unknown path → `<!-- IMAGE: original-src -->` placeholder, never silently drop.

---

## Two-Phase Workflow

### Phase 1 — Programmatic extraction (no LLM, run locally)

```bash
python3 skills/knowledge-panel-html/md2outline.py <input.md> <output.json>
```

`md2outline.py` parses the Markdown following the Input Contract and emits a
deterministic JSON outline.  It applies the Component Decision Rules in code,
so the LLM never needs to decide which component to use.

Output schema:
```json
{
  "title": "...",
  "description": "...",
  "images": [{"alt": "...", "src": "..."}],
  "sections": [
    {
      "id": "slug-01",
      "num": "01",
      "h2": "Section Title",
      "type": "cards|steps|table|code|alert|details|diff|prose|summary",
      "raw": "<verbatim section body in Markdown>",
      "items": "..."
    }
  ]
}
```

`items` is pre-parsed per type:
- **cards** → `[{"title", "body"}, ...]`
- **steps** → `[{"title", "body"}, ...]`
- **table** → `{"headers": [...], "rows": [[...]]}`
- **code** → `[{"lang", "content"}, ...]`
- **alert** → `{"variant": note|tip|warning|important|caution, "title": str, "blocks": [{"type":"p","text":str} | {"type":"ul","items":[str]}], "body": str}`
  - `title` — custom label from `> [!VARIANT] Title Text` (may be empty)
  - `blocks` — ordered content blocks; `"p"` → prose paragraph, `"ul"` → unordered list
  - `body` — flat back-compat string (prose + `- item` lines joined by `\n`)
- **details** → `[{"summary", "body"}, ...]`
- **prose / summary / diff** → cleaned string

### Phase 2 — LLM fills the template

Feed the LLM **only**:
1. The JSON outline from Phase 1 (≈60–80% smaller than the original Markdown)
2. This prompt:

```
You are filling the template `templates/github-style-panel.html`.

Rules:
- Copy the ENTIRE <style> block verbatim from the template. Do NOT regenerate CSS.
- For each section in the outline, use EXACTLY the component its `type` field specifies.
- section id attributes must match the outline `id` values exactly.
- Do not add components, wrappers, or classes beyond what the template defines.
- Preserve all images from the `images` array using .gh-figure.
- The last section with type "summary" must use .summary-panel (not .gh-section).

Alert rendering rules (applies to ALL .gh-alert blocks, regardless of section type):
- `.gh-alert__title` text = items.title if non-empty, else the default variant label (e.g. "💡 Tip").
- Render each block in `items.blocks` in order:
  - `{"type": "p"}` → `<p>text</p>`
  - `{"type": "ul"}` → `<ul><li>item</li>…</ul>`
- NEVER use `<br>` or bullet characters (•, -, *) as substitutes for list items.
- When rendering alerts from `raw` markdown in mixed sections, apply the same rule:
  any `- item` lines inside a `> ` blockquote must become `<ul><li>` elements.

Output a single self-contained HTML file.
```

