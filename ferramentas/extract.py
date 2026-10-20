"""Extract exam PDFs to clean, column-aware text.

usage: python3 -I extract.py <pdf_dir> <out_dir>
"""
import sys, os, re, pymupdf

NOISE = re.compile(r"pcimarkpci|pciconcursos|^www\.|^\s*$")


def page_lines(page):
    w = page.rect.width
    d = page.get_text("dict")
    lines = []
    for b in d["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            # skip rotated text (watermarks)
            dx, dy = l["dir"]
            if abs(dy) > 0.1:
                continue
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt or NOISE.search(txt):
                continue
            size = max(s["size"] for s in l["spans"])
            bold = any("Bold" in s["font"] or s["flags"] & 16 for s in l["spans"])
            x0, y0, x1, y1 = l["bbox"]
            lines.append((x0, y0, x1, y1, txt, size, bold))
    # detect two-column layout: lines that start right of center and do not cross it
    mid = w / 2
    right = [l for l in lines if l[0] > mid - 5]
    left_narrow = [l for l in lines if l[2] < mid + 15]
    full = [l for l in lines if l[0] < mid - 5 and l[2] > mid + 15]
    two_col = len(right) > 8 and len(left_narrow) > 8 and len(full) <= max(3, 0.12 * len(lines))
    if two_col:
        key = lambda l: (round(l[1] / 2), l[0])
        # split into vertical bands at full-width lines; inside a band: left col then right col
        out = []
        cuts = sorted(full, key=key)
        prev_y = -1
        for cut in cuts + [None]:
            y = cut[1] if cut else 1e9
            band = [l for l in lines if l not in full and prev_y <= l[1] < y]
            out += sorted([l for l in band if l[0] < mid - 5], key=key)
            out += sorted([l for l in band if l[0] >= mid - 5], key=key)
            if cut:
                out.append(cut)
            prev_y = y
    else:
        out = sorted(lines, key=lambda l: (round(l[1] / 2), l[0]))
    # merge fragments on same baseline
    merged = []
    for l in out:
        if merged and abs(merged[-1][1] - l[1]) < 2.5 and l[0] >= merged[-1][2] - 1 and (not two_col or (l[0] < mid) == (merged[-1][0] < mid)):
            p = merged[-1]
            merged[-1] = (p[0], p[1], l[2], max(p[3], l[3]), p[4] + " " + l[4], max(p[5], l[5]), p[6] or l[6])
        else:
            merged.append(l)
    return [m[4] for m in merged]


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not f.endswith(".pdf"):
            continue
        doc = pymupdf.open(os.path.join(src, f))
        chunks = []
        for i, page in enumerate(doc):
            chunks.append(f"\n<<<PAGE {i+1}>>>\n" + "\n".join(page_lines(page)))
        with open(os.path.join(dst, f[:-4] + ".txt"), "w") as fh:
            fh.write("".join(chunks))
        print(len(doc), f)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
