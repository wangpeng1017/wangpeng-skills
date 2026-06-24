"""
fix_header_footer.py
对 P02-P17 所有内容页做以下改动：
1. 删除顶部页眉文字"海克斯康华东方案中心  ·  NPI..."
2. 删除底部脚注文字"海克斯康华东方案中心  ·  ...接榜挂帅申报"
3. 把章节标签(badge)和页面标题移入顶部页眉条
4. 把页码从右上角(x=1220,y=46)移到左下角(x=60,y=695)
5. 删除标题下方的装饰下划线(y=110)
"""
import re, os

SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "svg_output")
SKIP = {"P01_cover.svg", "P18_closing.svg"}

def fix(content):
    # ── 1. 删除顶部页眉 org 文字 ────────────────────────────────────────────
    content = re.sub(
        r'\s*<text[^>]*x="60"[^>]*y="46"[^>]*>海克斯康[^<]*</text>',
        '', content)

    # ── 2. 删除底部脚注 ────────────────────────────────────────────────────
    content = re.sub(
        r'\s*<text[^>]*y="715"[^>]*>海克斯康[^<]*</text>',
        '', content)

    # ── 3. 页码：右上(x=1220,y=46) → 左下(x=60,y=695) ───────────────────
    content = re.sub(
        r'(<text\s[^>]*?)x="1220"([^>]*)y="46"([^>]*>(?:\d{1,2})<\/text>)',
        r'\1x="60"\2y="695"\3', content)
    # Also handle if y= comes before x=
    content = re.sub(
        r'(<text\s[^>]*?)y="46"([^>]*)x="1220"([^>]*>(?:\d{1,2})<\/text>)',
        r'\1y="695"\2x="60"\3', content)

    # ── 4a. 章节 badge rects: y="82" → y="27" ───────────────────────────
    # Two rects at y=82 with width=90 height=22
    content = re.sub(
        r'(<rect\s[^>]*?)y="82"([^>]*width="90"[^>]*height="22"[^/]*/\s*>)',
        r'\1y="27"\2', content)
    content = re.sub(
        r'(<rect\s[^>]*?width="90"[^>]*height="22"[^>]*?)y="82"([^/]*/\s*>)',
        r'\1y="27"\2', content)

    # ── 4b. 章节 badge 文字: y="97" → y="42" ───────────────────────────
    content = re.sub(
        r'(<text\s[^>]*?)y="97"([^>]*text-anchor="middle")',
        r'\1y="42"\2', content)
    content = re.sub(
        r'(<text\s[^>]*?text-anchor="middle"[^>]*?)y="97"',
        r'\1y="42"', content)

    # ── 4c. 页面标题: y="101" font-size="30" → y="50" font-size="24" ───
    # The title is x="164" y="101"
    content = re.sub(
        r'(<text\s[^>]*?)x="164"([^>]*)y="101"([^>]*)font-size="30"',
        r'\1x="170"\2y="50"\3font-size="24"', content)
    content = re.sub(
        r'(<text\s[^>]*?)font-size="30"([^>]*)x="164"([^>]*)y="101"',
        r'\1font-size="24"\2x="170"\3y="50"', content)
    content = re.sub(
        r'(<text\s[^>]*?)y="101"([^>]*)x="164"([^>]*)font-size="30"',
        r'\1y="50"\2x="170"\3font-size="24"', content)

    # ── 5. 删除 y=110 处的装饰下划线 ────────────────────────────────────
    content = re.sub(
        r'\s*<rect[^>]*y="110"[^>]*height="3"[^>]*/\s*>',
        '', content)

    return content


def main():
    files = sorted(f for f in os.listdir(SVG_DIR)
                   if f.endswith('.svg') and f not in SKIP)
    for fname in files:
        fp = os.path.join(SVG_DIR, fname)
        with open(fp, 'r', encoding='utf-8') as f:
            original = f.read()
        fixed = fix(original)
        if fixed != original:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(fixed)
            print(f"  ✓ {fname}")
        else:
            print(f"  - {fname} (no change)")
    print("Done.")

if __name__ == '__main__':
    main()
