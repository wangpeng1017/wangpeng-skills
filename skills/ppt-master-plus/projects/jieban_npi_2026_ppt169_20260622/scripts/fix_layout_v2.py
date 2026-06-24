"""
fix_layout_v2.py
三项布局修复：
1. P02: "目录 CONTENTS" 移入顶部页眉条（y=50），同步上移TOC内容
2. P02-P17 全部内容页: 正文主体上移 20 SVG units (≈15pt)
3. 普通内容页（非chapter opener）: 页面主标题下移 5 SVG units (≈4pt)，对齐badge中心
"""
import re, os

SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "svg_output")
SKIP = {"P01_cover.svg", "P18_closing.svg"}

CHAPTER_OPENERS = {
    "P03_ch1_opener.svg", "P06_ch2_opener.svg", "P09_ch3_opener.svg",
    "P11_ch4_opener.svg", "P14_ch5_opener.svg"
}

SHIFT = 20      # body content shifts up by this many SVG units
BODY_LO = 79   # shift if y > BODY_LO
BODY_HI = 650  # do NOT shift if y >= BODY_HI (logo/footer area)
TITLE_DROP = 5  # header title drops down by this many SVG units (≈4pt)


def shift_body(content, shift=SHIFT, lo=BODY_LO, hi=BODY_HI):
    """Decrease y-coordinates that are in the body range (lo, hi) by shift."""
    def _dec(val_str):
        v = float(val_str)
        if lo < v < hi:
            return str(int(round(v - shift)))
        return val_str

    def sub_y(m):
        new = _dec(m.group(1))
        return f'y="{new}"'

    def sub_cy(m):
        new = _dec(m.group(1))
        return f'cy="{new}"'

    def sub_y1(m):
        new = _dec(m.group(1))
        return f'y1="{new}"'

    def sub_y2(m):
        new = _dec(m.group(1))
        return f'y2="{new}"'

    content = re.sub(r'\by="(\d+(?:\.\d+)?)"', sub_y, content)
    content = re.sub(r'\bcy="(\d+(?:\.\d+)?)"', sub_cy, content)
    content = re.sub(r'\by1="(\d+(?:\.\d+)?)"', sub_y1, content)
    content = re.sub(r'\by2="(\d+(?:\.\d+)?)"', sub_y2, content)
    return content


def fix_p02_header(content):
    """Move 目录/CONTENTS title into the header strip at y=50."""
    # Move "目录" text: y=115 -> y=50
    content = re.sub(
        r'(<text\s[^>]*?)(\bx="60"\b)([^>]*)(\by="115"\b)([^>]*>目录</text>)',
        r'\1\2\3y="50"\5', content)
    # Move "CONTENTS" text: y=115 -> y=50, adjust x slightly
    content = re.sub(
        r'(<text\s[^>]*?)(\bx="160"\b)([^>]*)(\by="115"\b)([^>]*>CONTENTS</text>)',
        r'\1x="155"\3y="50"\5', content)
    # Remove decorative underline at y=125
    content = re.sub(r'\s*<rect[^>]*\by="125"\b[^>]*/\s*>', '', content)
    return content


def fix_title_down(content, drop=TITLE_DROP):
    """Move header page title (y=50 font-size=24) down by drop units."""
    def _shift_title(m):
        v = float(m.group(1))
        if abs(v - 50) < 0.5:
            return f'y="{int(round(v + drop))}"'
        return m.group(0)

    # Match y="50" only when near font-size="24" on the same element
    # Use a two-pass approach: find lines with both y=50 and font-size=24
    lines = content.split('\n')
    result = []
    for line in lines:
        if 'y="50"' in line and 'font-size="24"' in line:
            line = line.replace('y="50"', f'y="{50 + drop}"')
        result.append(line)
    return '\n'.join(result)


def main():
    files = sorted(f for f in os.listdir(SVG_DIR)
                   if f.endswith('.svg') and f not in SKIP)

    for fname in files:
        fp = os.path.join(SVG_DIR, fname)
        with open(fp, 'r', encoding='utf-8') as f:
            original = f.read()

        content = original

        if fname == "P02_agenda.svg":
            # Step 1: move 目录 title into header
            content = fix_p02_header(content)
            # Step 2: shift body content up
            content = shift_body(content)
        else:
            # All other content pages: shift body up
            content = shift_body(content)
            # Non-chapter-opener pages: also move header title down
            if fname not in CHAPTER_OPENERS:
                content = fix_title_down(content)

        if content != original:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {fname}")
        else:
            print(f"  - {fname} (no change)")

    print("Done.")


if __name__ == '__main__':
    main()
