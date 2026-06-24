"""
add_logo_to_content_pages.py
在 P02-P17 所有内容页底部右侧嵌入真实 HEXAGON 白色 logo 图片。
在 </svg> 前插入一行 <image> 元素。
"""
import os
import re

SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "svg_output")

LOGO_TAG = ('  <!-- HEXAGON logo white — bottom right -->\n'
            '  <image href="../images/hexagon_logo_white.png"'
            ' x="1090" y="650" width="148" height="48"'
            ' preserveAspectRatio="xMidYMid meet"/>\n\n')

# P01 and P18 are fully redesigned; skip them here
SKIP = {"P01_cover.svg", "P18_closing.svg"}

def add_logo(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has the logo image
    if 'hexagon_logo_white.png' in content:
        return False

    # Insert before </svg>
    content = content.replace('</svg>', LOGO_TAG + '</svg>', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def main():
    files = sorted(f for f in os.listdir(SVG_DIR)
                   if f.endswith('.svg') and f not in SKIP)
    changed, skipped = [], []
    for fname in files:
        fp = os.path.join(SVG_DIR, fname)
        if add_logo(fp):
            changed.append(fname)
        else:
            skipped.append(fname)

    print(f"Added logo to {len(changed)} files:")
    for f in changed:
        print(f"  ✓ {f}")
    if skipped:
        print(f"Already had logo / skipped: {skipped}")
    print("Done.")


if __name__ == '__main__':
    main()
