# Style Analysis — Light Explainer Panel

Source: screenshot attached to workspace session, 2026-03-13  
Subject: "AI Agent 是怎么工作的？" instructional slide / explainer page

---

## Color Tokens

| Token               | Value       | Usage                                      |
|---------------------|-------------|--------------------------------------------|
| `bg`                | `#F8FAFB`   | Page canvas                                |
| `surface`           | `#FFFFFF`   | Cards, panel boxes                         |
| `border`            | `#D6E8E6`   | Panel outlines, table rows                 |
| `primary`           | `#2A9D8F`   | Eyebrow badge, step numbers, icons, arrows |
| `primary-dark`      | `#1B7A70`   | Heading accent, badge text                 |
| `primary-dim`       | `#E4F4F2`   | Section-number ghost, badge background     |
| `flow-block-1..5`   | dark→light teal gradient | Context-window block sequence |
| `text`              | `#1A202C`   | Body headings                              |
| `text-muted`        | `#5A6A72`   | Caption, step desc, table cells            |
| `insight-bg`        | `#F0FAF9`   | Insight note background                    |

---

## Typography

- **Page font**: System sans-serif Chinese stack (`PingFang SC`, `Microsoft YaHei`, `-apple-system`)
- **Display headings**: `clamp(1.7rem, 3vw, 2.4rem)`, `font-weight: 800`
- **Section headings**: `1.25rem`, `font-weight: 800`
- **Mono labels / step desc**: `SFMono-Regular`, `Fira Code`, `Consolas`; `font-size: .75rem`
- **Body**: `15px`, `line-height: 1.7`

---

## Component Inventory

### Eyebrow Badge
- Rounded pill, `border: 1.5px solid primary`, teal background
- Contains inline SVG icon + category text
- Lives above `<h1>` hero title

### Context-Window Panel Box
- Bordered box (`border: 1.5px solid border`, `border-radius: 18px`)
- Contains a scrollable horizontal list of **flow blocks**
- Flow blocks: 5 boxes, dark-to-light teal gradient, show title + subtitle

### Decision / Process Flow
- Horizontal ordered list of numbered step cards
- Cards connected by `→` pseudo-element arrows
- Last step highlighted with teal border + teal-dim background
- Falls back to vertical column on mobile with `↓` arrow

### Insight Note
- Left teal border bar, teal-tinted background
- Italic muted text with bold callout prefix
- Lives directly below the process flow

### Feature Card Grid
- 4-column auto-fill grid
- Each card: SVG icon (teal), mono `fc__title`, muted `fc__desc`
- Top border accent on hover (`border-color: primary`)

---

## Layout

- Single-column centered layout (max-width `900px`)
- No sidebar in this template (contrast: dark-navy variant uses fixed sidebar)
- Sections separated by top border dividers + vertical gap

---

## Animations / Motion

- None in this style — content is meant to feel like a clean slide/document
- Optional: add `.fade-up` scroll-reveal if desired (not present in source)

---

## MUST Refer to the template - `github-style-panel.html`
