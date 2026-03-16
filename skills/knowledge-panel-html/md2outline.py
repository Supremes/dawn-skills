#!/usr/bin/env python3
"""
md2outline.py — Phase 1: Markdown → JSON Outline
─────────────────────────────────────────────────
Parses a structured Markdown file (following the Input Contract in SKILL.md)
and emits a deterministic JSON outline.  Feed the outline to the LLM as
Phase-2 input instead of the full Markdown + template — saves ~60-80% tokens.

Usage:
    python3 md2outline.py <input.md> [output.json]
    python3 md2outline.py <input.md>          # prints JSON to stdout

Output schema:
    {
      "title":       str,
      "description": str,
      "sections": [
        {
          "id":    "section-01",
          "num":   "01",
          "h2":    str,
          "type":  "cards|steps|table|code|alert|details|diff|prose|summary",
          "raw":   str,         # verbatim section body (Markdown)
          "items": list | None  # pre-parsed items when type is structured
        },
        ...
      ]
    }

items shape per type:
    cards  → [{"title": str, "body": str}, ...]
    steps  → [{"title": str, "body": str}, ...]
    table  → {"headers": [str], "rows": [[str]]}
    code   → [{"lang": str, "content": str}, ...]
    alert  → {"variant": note|tip|warning|important|caution, "title": str,
              "blocks": [{"type": "p", "text": str} | {"type": "ul", "items": [str]}],
              "body": str}   # flat back-compat string
    diff   → str  (raw diff lines, no further parsing)
    details→ [{"summary": str, "body": str}, ...]
    prose  → str  (cleaned paragraph text)
    summary→ str  (raw body)
"""

import re
import sys
import json
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    """Convert heading text to a lowercase dash-separated id slug."""
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    text = re.sub(r'\s+', '-', text.strip().lower())
    return text or 'section'


def _strip_inline(text: str) -> str:
    """Remove Markdown inline markup (bold, italic, code, links)."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    return text.strip()


# ── Section splitter ──────────────────────────────────────────────────────────

def _split_sections(lines: list[str]) -> tuple[str, str, list[tuple[str, list[str]]]]:
    """
    Returns (title, description, [(h2_raw_line, body_lines), ...]).
    title       — first `# ` line (stripped)
    description — first `> ` line (stripped of `> `)
    """
    title = ''
    description = ''
    sections: list[tuple[str, list[str]]] = []
    current_h2 = None
    current_body: list[str] = []

    for line in lines:
        if not title and line.startswith('# '):
            title = _strip_inline(line[2:])
            continue

        if not description and current_h2 is None and line.startswith('> ') and not line.startswith('> [!'):
            description = line[2:].strip()
            continue

        if line.startswith('## '):
            if current_h2 is not None:
                sections.append((current_h2, current_body))
            current_h2 = line
            current_body = []
        elif current_h2 is not None:
            current_body.append(line)

    if current_h2 is not None:
        sections.append((current_h2, current_body))

    return title, description, sections


# ── Type detection (Component Decision Rules) ─────────────────────────────────

_ALERT_MAP = {
    # GitHub official variants
    'NOTE': 'note', 'TIP': 'tip', 'WARNING': 'warning',
    'IMPORTANT': 'important', 'CAUTION': 'caution',
    # Common community aliases → nearest GitHub Primer colour
    'INFO':     'note',       # blue
    'ABSTRACT': 'important',  # purple
    'DANGER':   'caution',    # red
    'SUCCESS':  'tip',        # green
    'QUOTE':    'note',       # blue
    'EXAMPLE':  'note',       # blue
}

_SUMMARY_KEYWORDS = re.compile(
    r'^(总结|summary|tl;dr|tldr|executive\s+summary|结语|conclusion)$',
    re.IGNORECASE,
)


def _detect_type(h2_line: str, body_lines: list[str], is_last: bool) -> str:
    """Apply the first-match decision table from SKILL.md."""

    # 0. Inline type override
    m = re.search(r'<!--\s*type:\s*(\w+)\s*-->', h2_line, re.IGNORECASE)
    if m:
        return m.group(1).lower()

    h2_text = re.sub(r'##\s*', '', h2_line).strip()
    h2_text = re.sub(r'<!--.*?-->', '', h2_text).strip()

    # 1. Last section with summary keyword
    if is_last and _SUMMARY_KEYWORDS.match(h2_text):
        return 'summary'

    body = '\n'.join(body_lines)

    # 2. Diff block signal — fenced ```diff OR git diff header (--- a/path / +++ b/path)
    # NOTE: bare `---` horizontal rules must NOT match; require a non-whitespace char after the space.
    if re.search(r'```diff', body) or re.search(r'^(?:---|\+\+\+) \S', body, re.M):
        return 'diff'

    # 3. Fenced code block as primary content (>40% of non-empty lines)
    code_lines = len(re.findall(r'```', body)) // 2
    non_empty = [l for l in body_lines if l.strip()]
    inside_fence = False
    fence_line_count = 0
    for l in body_lines:
        if l.startswith('```'):
            inside_fence = not inside_fence
        elif inside_fence:
            fence_line_count += 1
    if non_empty and fence_line_count / max(len(non_empty), 1) > 0.4 and code_lines >= 1:
        return 'code'

    # 4. Markdown table
    if re.search(r'^\|.+\|', body, re.M) and re.search(r'^\|[-| :]+\|', body, re.M):
        return 'table'

    # 5. Ordered list = steps  (checked before alert — steps are primary content)
    if re.search(r'^\d+\.\s', body, re.M):
        return 'steps'

    # 6. GitHub-style alert blockquote — only when it IS the sole primary content.
    #    Requires: exactly 1 alert, no H3 sub-sections, no embedded images, ≤1 outer prose line.
    alert_matches = re.findall(r'^>\s*\[!\w+\]', body, re.M)
    if (len(alert_matches) == 1
            and not re.search(r'^#{3}', body, re.M)
            and not re.search(r'!\[', body)):
        m = re.search(r'^>\s*\[!(\w+)\]', body, re.M)
        if m and m.group(1).upper() in _ALERT_MAP:
            outer_prose = [
                l for l in body_lines
                if l.strip()
                and not l.startswith('>')
                and not l.startswith('!')
                and not l.startswith('#')
                and not re.match(r'^\s*[-*+]\s', l)
                and not l.startswith('```')
                and not l.startswith('|')
            ]
            if len(outer_prose) <= 1:
                return 'alert'

    # 7. <details> block
    if '<details' in body.lower():
        return 'details'

    # 8. ≥3 H3 headings each with 2-5 lines of body → cards
    h3_positions = [i for i, l in enumerate(body_lines) if l.startswith('### ')]
    if len(h3_positions) >= 3:
        qualifying = 0
        for idx, pos in enumerate(h3_positions):
            next_pos = h3_positions[idx + 1] if idx + 1 < len(h3_positions) else len(body_lines)
            body_under = [l for l in body_lines[pos + 1:next_pos] if l.strip()]
            if 1 <= len(body_under) <= 7:
                qualifying += 1
        if qualifying >= 3:
            return 'cards'

    return 'prose'


# ── Item parsers ──────────────────────────────────────────────────────────────

def _parse_cards(body_lines: list[str]) -> list[dict]:
    """H3-based cards: each ### heading → {title, body}."""
    cards = []
    current_title = None
    current_body: list[str] = []

    def _flush():
        if current_title:
            cards.append({'title': current_title,
                          'body': ' '.join(l.strip() for l in current_body if l.strip())})

    for line in body_lines:
        if line.startswith('### '):
            _flush()
            current_title = _strip_inline(line[4:])
            current_body = []
        elif current_title is not None:
            current_body.append(line)

    _flush()
    return cards


def _parse_steps(body_lines: list[str]) -> list[dict]:
    """Ordered-list steps: 1. Title\\n   description → {title, body}."""
    steps = []
    current: dict | None = None

    for line in body_lines:
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            if current:
                steps.append(current)
            current = {'title': _strip_inline(m.group(1)), 'body': ''}
        elif current and line.strip():
            sep = ' ' if current['body'] else ''
            current['body'] += sep + line.strip()

    if current:
        steps.append(current)

    return steps


def _parse_table(body_lines: list[str]) -> dict:
    """Extract Markdown table into {headers: [...], rows: [[...]]}."""
    headers: list[str] = []
    rows: list[list[str]] = []

    for line in body_lines:
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if re.match(r'^[-: ]+$', cells[0]):
            continue        # separator row
        if not headers:
            headers = [_strip_inline(c) for c in cells]
        else:
            rows.append([_strip_inline(c) for c in cells])

    return {'headers': headers, 'rows': rows}


def _parse_code(body_lines: list[str]) -> list[dict]:
    """Extract all fenced code blocks: [{lang, content}, ...]."""
    blocks = []
    in_fence = False
    lang = ''
    buf: list[str] = []

    for line in body_lines:
        if not in_fence and line.startswith('```'):
            in_fence = True
            lang = line[3:].strip()
            buf = []
        elif in_fence and line.startswith('```'):
            in_fence = False
            blocks.append({'lang': lang, 'content': '\n'.join(buf)})
        elif in_fence:
            buf.append(line)

    return blocks


def _parse_alert(body_lines: list[str]) -> dict:
    """Extract > [!VARIANT] blockquote alert with structured body blocks.

    Returns:
        variant   — CSS modifier (note|tip|warning|important|caution)
        title     — custom title text from > [!VARIANT] Title Text line
        blocks    — list of {"type": "p", "text": str} or {"type": "ul", "items": [str]}
        body      — flat back-compat string (prose + "- item" lines joined by \\n)
    """
    variant = 'note'
    title = ''
    blocks: list[dict] = []
    prose_buf: list[str] = []
    list_buf: list[str] = []

    def _flush_prose() -> None:
        text = ' '.join(prose_buf).strip()
        if text:
            blocks.append({'type': 'p', 'text': text})
        prose_buf.clear()

    def _flush_list() -> None:
        if list_buf:
            blocks.append({'type': 'ul', 'items': list(list_buf)})
        list_buf.clear()

    for line in body_lines:
        m_variant = re.match(r'^>\s*\[!(\w+)\]\s*(.*)', line)
        if m_variant:
            variant = _ALERT_MAP.get(m_variant.group(1).upper(), 'note')
            title_text = _strip_inline(m_variant.group(2).strip())
            if title_text:
                title = title_text
            continue

        if line.startswith('> '):
            content = line[2:].strip()
        elif line.strip() == '>':
            content = ''
        else:
            continue

        m_li = re.match(r'^[-*+]\s+(.*)', content)
        if m_li:
            # List item — flush any pending prose first
            _flush_prose()
            list_buf.append(_strip_inline(m_li.group(1)))
        elif content:
            # Prose line — flush any pending list first
            _flush_list()
            prose_buf.append(_strip_inline(content))
        else:
            # Blank line — flush both buffers
            _flush_prose()
            _flush_list()

    _flush_prose()
    _flush_list()

    # Build flat back-compat body string
    flat_parts: list[str] = []
    for b in blocks:
        if b['type'] == 'p':
            flat_parts.append(b['text'])
        elif b['type'] == 'ul':
            flat_parts.extend(f'- {it}' for it in b['items'])

    return {
        'variant': variant,
        'title': title,
        'blocks': blocks,
        'body': '\n'.join(flat_parts),
    }


def _parse_details(body_lines: list[str]) -> list[dict]:
    """Extract <details>/<summary> blocks."""
    items = []
    current_summary = ''
    current_body: list[str] = []
    in_details = False
    in_body = False

    for line in body_lines:
        if re.match(r'<details', line, re.IGNORECASE):
            in_details = True
            current_summary = ''
            current_body = []
            in_body = False
        elif in_details:
            summary_m = re.search(r'<summary>(.*?)<\/summary>', line, re.IGNORECASE)
            if summary_m:
                current_summary = _strip_inline(summary_m.group(1))
                in_body = True
            elif re.match(r'</details', line, re.IGNORECASE):
                items.append({'summary': current_summary,
                               'body': '\n'.join(current_body).strip()})
                in_details = False
                in_body = False
            elif in_body:
                current_body.append(line)

    return items


def _parse_prose(body_lines: list[str]) -> str:
    """Return cleaned paragraph text."""
    paragraphs: list[str] = []
    current: list[str] = []

    for line in body_lines:
        if line.strip():
            current.append(_strip_inline(line))
        else:
            if current:
                paragraphs.append(' '.join(current))
                current = []

    if current:
        paragraphs.append(' '.join(current))

    return '\n\n'.join(paragraphs)


# ── Section builder ───────────────────────────────────────────────────────────

def _build_section(h2_line: str, body_lines: list[str], index: int, is_last: bool) -> dict:
    num = f'{index + 1:02d}'

    # Strip `## ` prefix and any inline type comment for display text
    h2_text = re.sub(r'^##\s*', '', h2_line).strip()
    h2_text = re.sub(r'<!--.*?-->', '', h2_text).strip()
    h2_text = _strip_inline(h2_text)

    section_type = _detect_type(h2_line, body_lines, is_last)
    raw = '\n'.join(body_lines).strip()

    # Parse items based on type
    items = None
    if section_type == 'cards':
        items = _parse_cards(body_lines)
    elif section_type == 'steps':
        items = _parse_steps(body_lines)
    elif section_type == 'table':
        items = _parse_table(body_lines)
    elif section_type == 'code':
        items = _parse_code(body_lines)
    elif section_type == 'alert':
        items = _parse_alert(body_lines)
    elif section_type == 'details':
        items = _parse_details(body_lines)
    elif section_type in ('prose', 'summary', 'diff'):
        items = _parse_prose(body_lines)

    # Build section id: prefer slug, fallback to section-NN
    slug = _slug(h2_text)
    section_id = f'{slug}-{num}' if slug and slug != 'section' else f'section-{num}'

    return {
        'id': section_id,
        'num': num,
        'h2': h2_text,
        'type': section_type,
        'raw': raw,
        'items': items,
    }


# ── Image extractor ───────────────────────────────────────────────────────────

def _extract_images(lines: list[str]) -> list[dict]:
    """Find all ![alt](src) references in the document."""
    images = []
    for line in lines:
        for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', line):
            images.append({'alt': m.group(1), 'src': m.group(2)})
    return images


# ── Main parser ───────────────────────────────────────────────────────────────

def parse(md_path: str) -> dict:
    text = Path(md_path).read_text(encoding='utf-8')
    lines = text.splitlines()

    title, description, raw_sections = _split_sections(lines)
    images = _extract_images(lines)

    sections = []
    for i, (h2_line, body_lines) in enumerate(raw_sections):
        is_last = (i == len(raw_sections) - 1)
        sections.append(_build_section(h2_line, body_lines, i, is_last))

    return {
        'title': title,
        'description': description,
        'images': images,
        'sections': sections,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 md2outline.py <input.md> [output.json]', file=sys.stderr)
        sys.exit(1)

    md_path = sys.argv[1]
    outline = parse(md_path)
    out = json.dumps(outline, ensure_ascii=False, indent=2)

    if len(sys.argv) >= 3:
        Path(sys.argv[2]).write_text(out, encoding='utf-8')
        print(f'✓ Outline written to {sys.argv[2]}')
        print(f'  sections : {len(outline["sections"])}')
        print(f'  images   : {len(outline["images"])}')
        types = [s["type"] for s in outline["sections"]]
        for t in sorted(set(types)):
            print(f'    {t:12s} × {types.count(t)}')
    else:
        print(out)


if __name__ == '__main__':
    main()
