---
name: knowledge-panel-html
description: "Use when creating or refactoring long-form HTML knowledge pages, technical explainer pages, protocol overviews, study notes, visual reference pages, or when the user asks to parse an existing HTML page style and generate a reusable template. Keywords: HTML 页面风格分析, 可复用模板, agent skill, 技术长文, 知识展板, 专题页, GitHub Primer 风格页面, knowledge panel, docs page."
---

# Knowledge Panel HTML

This skill generates polished, self-contained HTML knowledge pages using the **GitHub Primer light** visual style.

Use this skill when the task is to:
- generate a new long-form HTML page from Markdown or rough notes
- convert topic notes into a polished single-file technical showcase page
- keep the layout and information density consistent across multiple topic pages

## Design DNA

The target style follows GitHub's Primer design system:
- white `#ffffff` canvas with `#f6f8fa` subtle surfaces and `#d0d7de` borders
- two-column layout: main content (left, wider) · 296 px sticky sidebar (right)
- repo-style header: title + one-line description
- GitHub Primer 5-variant alert boxes: Note / Tip / Important / Warning / Caution
- dark code blocks (`#161b22`) with GitHub VS Code–like syntax colours
- diff blocks with +/– green/red line highlighting
- flat 6 px-radius cards — border + glow on hover, no drop shadows
- collapsible `<details>` / `<summary>` blocks
- sticky sidebar: TOC with active-link JS · About description box
- clean & utilitarian — no particles, no glassmorphism, no heavy motion
- fully responsive: single-column on ≤ 768 px (sidebar moves above content)

## Required Structure

When generating a page, follow this macro structure:

1. `<header class="repo-header">` — title + description only.
2. `.gh-layout` two-column grid:
   - **Left / main** (`.gh-content`): numbered `<section class="gh-section">` blocks.
   - **Right / sidebar** (`.gh-sidebar`): TOC box first, then About box.
3. Inside each section, mix content modules by topic:
   - feature card grids (`.gh-card-grid`)
   - numbered step lists (`.gh-step-list`)
   - comparison tables (`.gh-table-wrap / .gh-table`)
   - dark code panels (`.gh-code-block`)
   - diff blocks (`.gh-diff`)
   - alert callouts (`.gh-alert --note/tip/important/warning/caution`)
   - collapsible details (`.gh-details`)
4. Close with a summary panel (`.summary-panel`).
5. Minimal JS: scroll-spy active TOC link + copy-code button.

## Style Rules

Follow these rules exactly:
- Typography: system sans-serif body, monospace for code/labels.
- Palette: use only the `--gh-*` CSS variables already defined in `:root`.
- Layout: do not add extra wrappers; use the grid and gap variables.
- Components: only use classes defined in the template's `<style>` block.
- Motion: none beyond the 0.15 s border transition on cards and TOC hover.

## Image Handling

When the source Markdown contains images (`![alt](url)`), **always preserve them** in the generated HTML.

Rules:
- Scan the entire source file for all `![alt](url)` image references before generating HTML.
- For **remote URLs** (`http://` / `https://`): embed directly as `<img src="url" alt="alt">`.
- For **local relative paths** (e.g. `./img/foo.png`): use the path as-is; note it only works when the HTML is served from the same directory.
- Wrap every image in `.gh-figure` (defined in the template `<style>` block). Add `.gh-figure__caption` if the source provides meaningful alt text or surrounding caption text.
- Place the figure at the same logical position in the HTML as the image appears in the Markdown (i.e. within its surrounding section/paragraph context).
- Never silently drop images — if you cannot determine the path, include a visible `<!-- IMAGE: original-src -->` placeholder comment so the author can fix it manually.

Component usage:
```html
<figure class="gh-figure">
  <img src="https://example.com/image.webp" alt="AQS 内部结构" />
  <figcaption class="gh-figure__caption">图：AQS 宏观内部结构</figcaption>
</figure>
```

## Content Mapping Guidance

Map content into modules based on semantics:
- concept definitions -> two-column cards
- lifecycle or protocol flow -> ordered flow steps or code block sequence
- standards comparison -> table
- recommendations or risk levels -> badge + bordered cards
- future directions -> compact trend cards
- executive summary -> highlighted closing summary box

## Output Expectations

When using this skill for a new page:
- prefer a single self-contained HTML file unless the user requests extraction
- keep CSS variables at the top for easy theming
- preserve semantic section ids for sidebar navigation
- make the page immediately viewable in a browser without build tooling
- adapt copy to the new topic instead of mechanically cloning the original page

## Template

The single template is `templates/github-style-panel.html`.

### ⚠️ Strict Component Constraint

**Only use CSS classes that are explicitly defined in the chosen template's `<style>` block.**

- Do NOT invent new component classes (e.g. `gh-badge`, `stat-row`, `lang-box`, `lang-bar`) even if they are mentioned in the template's comment/description.
- Do NOT copy components from a different template into the generated file.
- The template's COMPONENT QUICK-REF is the authoritative list of available classes. Components listed there but absent from the `<style>` block are documentation notes only — do not implement them.
- If a content need cannot be met by an existing template component, adapt the closest available component rather than creating a new one.

Template: `templates/github-style-panel.html` — GitHub Primer light, two-column docs layout.

## Implementation Notes

- Keep inline CSS and JS if the output is meant to be portable.
- If the user already has a site design system, port only the information architecture and section modules, not the full color system.
- If the user asks for a lighter variant, keep the same structure but swap the palette instead of changing the layout grammar.