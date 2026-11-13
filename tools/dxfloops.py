"""Split a CSK spec DXF's LINE/ARC entities into connected chains.

Used by genfp.py. Run on its own to list a DXF's chains:
usage: dxfloops.py file.dxf
Units in the DXF are inches; output is mm with the origin at the outline's
bottom-left. Each chain is reported with whether it closes, its extent and
area, so the board outline can be told from keepout boxes.
"""
import math
import sys

IN = 25.4


def read(path):
    lines = open(path, errors="replace").read().splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    ents, cur, on = [], None, False
    for c, v in pairs:
        if c == "2" and v == "ENTITIES":
            on = True
            continue
        if on and c == "0":
            if cur:
                ents.append(cur)
            if v == "ENDSEC":
                break
            cur = {"t": v, "k": {}}
            continue
        if on and cur is not None and c in ("10", "20", "11", "21", "40", "50", "51"):
            cur["k"][c] = float(v)
    return ents


def edges(ents):
    """Each edge: dict with kind, start, end (inches) and arc params."""
    out = []
    for e in ents:
        k = e["k"]
        if e["t"] == "LINE":
            out.append({"kind": "line", "a": (k["10"], k["20"]), "b": (k["11"], k["21"])})
        elif e["t"] == "ARC":
            cx, cy, r, a0, a1 = k["10"], k["20"], k["40"], k["50"], k["51"]
            if a1 <= a0:
                a1 += 360
            am = (a0 + a1) / 2
            pt = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            out.append({"kind": "arc", "a": pt(a0), "m": pt(am), "b": pt(a1), "c": (cx, cy), "r": r, "a0": a0, "a1": a1})
    return out


def chains(es, tol=1e-4):
    left = list(range(len(es)))
    result = []
    while left:
        chain = [(left.pop(0), False)]
        grew = True
        while grew:
            grew = False
            head = es[chain[0][0]]["b" if chain[0][1] else "a"]
            tail = es[chain[-1][0]]["a" if chain[-1][1] else "b"]
            for i in list(left):
                e = es[i]
                if math.dist(e["a"], tail) < tol:
                    chain.append((i, False)); left.remove(i); grew = True; break
                if math.dist(e["b"], tail) < tol:
                    chain.append((i, True)); left.remove(i); grew = True; break
                if math.dist(e["b"], head) < tol:
                    chain.insert(0, (i, False)); left.remove(i); grew = True; break
                if math.dist(e["a"], head) < tol:
                    chain.insert(0, (i, True)); left.remove(i); grew = True; break
        result.append(chain)
    return result


def polyline(es, chain, step=2):
    pts = []
    for i, rev in chain:
        e = es[i]
        if e["kind"] == "line":
            seg = [e["a"], e["b"]]
        else:
            n = max(2, int((e["a1"] - e["a0"]) / step))
            seg = [(e["c"][0] + e["r"] * math.cos(math.radians(e["a0"] + (e["a1"] - e["a0"]) * j / n)),
                    e["c"][1] + e["r"] * math.sin(math.radians(e["a0"] + (e["a1"] - e["a0"]) * j / n))) for j in range(n + 1)]
        if rev:
            seg = seg[::-1]
        pts += seg if not pts else seg[1:]
    return pts


if __name__ == "__main__":
    es = edges(read(sys.argv[1]))
    cs = chains(es)
    allp = [p for e in es for p in (e["a"], e["b"])]
    x0, y0 = min(p[0] for p in allp), min(p[1] for p in allp)
    print(f"{len(es)} edges in {len(cs)} chains; origin (in) {x0:.4f},{y0:.4f}")
    for n, ch in enumerate(sorted(cs, key=len, reverse=True)):
        pts = [((x - x0) * IN, (y - y0) * IN) for x, y in polyline(es, ch)]
        closed = math.dist(pts[0], pts[-1]) < 0.01
        area = 0.5 * abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        kinds = sum(1 for i, _ in ch if es[i]["kind"] == "arc")
        print(f"chain {n}: {len(ch)} edges ({kinds} arcs), closed={closed}, gap {math.dist(pts[0], pts[-1]):.3f} mm, "
              f"x {min(xs):.2f}..{max(xs):.2f} y {min(ys):.2f}..{max(ys):.2f}, area {area:.0f} mm2")
