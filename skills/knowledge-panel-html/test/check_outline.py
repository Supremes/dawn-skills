import json, sys

d = json.loads(open('test/jmm-outline.json').read())
print('title:', d['title'])
print('description:', d['description'])
print()
for s in d['sections']:
    print(f"  [{s['num']}] {s['type']:10s}  id={s['id']}  h2={s['h2']}")
    if s['type'] == 'cards' and s['items']:
        for c in s['items']:
            print(f"        card: {c['title']}")
    elif s['type'] == 'steps' and s['items']:
        for st in s['items']:
            print(f"        step: {st['title']}")
    elif s['type'] == 'table' and s['items']:
        print(f"        headers: {s['items']['headers']}")
        print(f"        rows   : {len(s['items']['rows'])} rows")
    elif s['type'] == 'code' and s['items']:
        for cb in s['items']:
            lines = cb['content'].count('\n') + 1
            print(f"        code block: lang={cb['lang']}  {lines} lines")
    elif s['type'] == 'alert' and s['items']:
        body_preview = s['items']['body'][:60]
        print(f"        variant={s['items']['variant']}  body={body_preview}...")
    elif s['type'] == 'details' and s['items']:
        for dt in s['items']:
            print(f"        details: {dt['summary']}")
