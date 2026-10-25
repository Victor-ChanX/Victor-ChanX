#!/usr/bin/env python3
"""Generate an animated "chat window" SVG for the GitHub profile README.

Messages pop in one by one; before each of Victor's replies a typing
indicator shows, like a real-time chat. Pure SVG + CSS, no JS, so it
animates when GitHub embeds it as an <img>.
"""
import html
import sys

W = 860
PAD = 28
FONT = 15
LINE_H = 22
BUBBLE_PX = 16
BUBBLE_PY = 11
GAP = 14
HEADER_H = 64
MAX_BUBBLE_W = 520

# (who, text-lines)  who: "them" | "me"
CONVO = [
    ("them", ["hey 👋 who's this?"]),
    ("me",   ["Hi, I'm Victor — a full-stack dev based in the UK 🇬🇧"]),
    ("them", ["what do you build?"]),
    ("me",   ["AI-powered products & real-time communication tools 🎙️",
              "chat, voice, and agents that join the conversation 🤖"]),
    ("them", ["any open source?"]),
    ("me",   ["sogna-virtual-list ⚡ a React virtual list that keeps",
              "the scroll steady while messages stream in"]),
    ("them", ["ok… you really like chat apps 😂"]),
    ("me",   ["guilty. even this README is a chat 😎"]),
]

THEMES = {
    "dark": dict(
        bg="#0d1117", win="#161b22", border="#30363d", header="#1c2128",
        text="#e6edf3", sub="#8b949e", them="#21262d", them_text="#e6edf3",
        me="#2f81f7", me_text="#ffffff", dot="#8b949e", online="#3fb950",
    ),
    "light": dict(
        bg="#ffffff", win="#f6f8fa", border="#d0d7de", header="#ffffff",
        text="#1f2328", sub="#656d76", them="#ffffff", them_text="#1f2328",
        me="#0969da", me_text="#ffffff", dot="#8c959f", online="#1a7f37",
    ),
}


def text_width(s: str) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o in (0xFE0F, 0x200D):
            continue
        if 0x1F1E6 <= o <= 0x1F1FF:  # regional indicator: flag = 2 of these
            w += 10
        elif o > 0x2500:
            w += 20
        elif ch in "il.,'|!:;":
            w += 4.2
        elif ch in "mwMW":
            w += 12.5
        elif ch.isupper():
            w += 9.6
        elif ch == " ":
            w += 4.2
        else:
            w += 8.0
    return w


def build(theme: str) -> str:
    t = THEMES[theme]
    y = HEADER_H + 26
    items = []
    clock = 0.6  # seconds
    for who, lines in CONVO:
        bw = min(MAX_BUBBLE_W, max(text_width(l) for l in lines) + BUBBLE_PX * 2)
        bh = len(lines) * LINE_H + BUBBLE_PY * 2 - 4
        if who == "me":
            # typing indicator first, at the same spot
            items.append(("typing", y, clock, clock + 1.1))
            clock += 1.1
            x = W - PAD - 20 - bw
        else:
            x = PAD + 20
        items.append((who, x, y, bw, bh, lines, clock))
        clock += 1.0 if who == "me" else 0.9
        y += bh + GAP
    H = y + 20

    css = f"""
    .bubble {{ opacity:0; animation: pop .35s cubic-bezier(.2,.9,.3,1.3) forwards; }}
    .typing {{ opacity:0; animation: blink-in var(--d) linear forwards; }}
    .dot {{ animation: bounce 1s infinite ease-in-out; }}
    .dot:nth-child(2) {{ animation-delay:.15s }}
    .dot:nth-child(3) {{ animation-delay:.3s }}
    .status-typing {{ opacity:0; animation: status var(--d) linear forwards; }}
    @keyframes pop {{ 0% {{opacity:0; transform: translateY(10px) scale(.96)}} 100% {{opacity:1; transform:none}} }}
    @keyframes blink-in {{ 0% {{opacity:0}} 8% {{opacity:1}} 92% {{opacity:1}} 100% {{opacity:0}} }}
    @keyframes status {{ 0% {{opacity:0}} 5% {{opacity:1}} 95% {{opacity:1}} 100% {{opacity:0}} }}
    @keyframes bounce {{ 0%,60%,100% {{transform:translateY(0)}} 30% {{transform:translateY(-4px)}} }}
    @keyframes pulse {{ 0%,100% {{opacity:1}} 50% {{opacity:.35}} }}
    .live {{ animation: pulse 2s infinite; }}
    text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace; }}
    """

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Chat: Hi, I am Victor, a full-stack developer in the UK building AI-powered products and real-time communication tools.">')
    out.append(f"<style>{css}</style>")
    # window
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{t["win"]}" stroke="{t["border"]}"/>')
    out.append(f'<path d="M1 17a16 16 0 0 1 16-16h{W-34}a16 16 0 0 1 16 16v{HEADER_H-16}H1z" fill="{t["header"]}"/>')
    out.append(f'<line x1="1" y1="{HEADER_H}" x2="{W-1}" y2="{HEADER_H}" stroke="{t["border"]}"/>')
    # traffic lights
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        out.append(f'<circle cx="{26 + i*20}" cy="{HEADER_H/2}" r="6" fill="{c}"/>')
    # channel title
    out.append(f'<text x="{W/2}" y="{HEADER_H/2 - 3}" text-anchor="middle" font-size="16" font-weight="600" fill="{t["text"]}"># say-hi-to-victor</text>')
    # status line: "online" normally, "Victor is typing…" while typing
    sy = HEADER_H/2 + 16
    out.append(f'<g><circle class="live" cx="{W/2 - 30}" cy="{sy - 4}" r="4" fill="{t["online"]}"/>'
               f'<text x="{W/2 - 20}" y="{sy}" font-size="12" fill="{t["sub"]}">online</text></g>')
    # right header: tiny ws badge
    out.append(f'<text class="mono" x="{W - 24}" y="{HEADER_H/2 + 4}" text-anchor="end" font-size="12" fill="{t["sub"]}">ws://connected</text>')

    for it in items:
        if it[0] == "typing":
            _, ty, start, end = it
            dur = end - start
            # header status swaps "online" for "Victor is typing…"
            out.append(f'<g class="status-typing" style="--d:{dur}s; animation-delay:{start}s">'
                       f'<rect x="{W/2 - 90}" y="{sy - 14}" width="180" height="18" fill="{t["header"]}"/>'
                       f'<text x="{W/2}" y="{sy}" text-anchor="middle" font-size="12" font-style="italic" fill="{t["me"]}">Victor is typing…</text></g>')
            bw, bh = 64, 38
            x = W - PAD - 20 - bw
            dots = "".join(
                f'<circle class="dot" cx="{x + 18 + k*14}" cy="{ty + bh/2}" r="4" fill="{t["dot"]}"/>'
                for k in range(3))
            out.append(f'<g class="typing" style="--d:{dur}s; animation-delay:{start}s">'
                       f'<rect x="{x}" y="{ty}" width="{bw}" height="{bh}" rx="18" fill="{t["them"]}" stroke="{t["border"]}"/>'
                       f'<g>{dots}</g></g>')
            continue
        who, x, by, bw, bh, lines, start = it
        mine = who == "me"
        fill = t["me"] if mine else t["them"]
        tc = t["me_text"] if mine else t["them_text"]
        stroke = "none" if mine else t["border"]
        # tail corner: square the corner on the speaker's side
        g = [f'<g class="bubble" style="animation-delay:{start:.2f}s; transform-origin:{x + (bw if mine else 0)}px {by + bh}px">']
        g.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="{fill}" stroke="{stroke}"/>')
        cx = x + bw - 18 if mine else x
        g.append(f'<rect x="{cx}" y="{by + bh - 18}" width="18" height="18" fill="{fill}"/>')
        if not mine:
            # redraw border bits for the squared corner
            g.append(f'<path d="M{x} {by + bh - 18}V{by + bh}H{x + 18}" fill="none" stroke="{stroke}"/>')
        for i, line in enumerate(lines):
            ly = by + BUBBLE_PY + 15 + i * LINE_H
            g.append(f'<text x="{x + BUBBLE_PX}" y="{ly}" font-size="{FONT}" fill="{tc}">{html.escape(line)}</text>')
        # avatar
        ax = W - PAD + 2 if mine else PAD + 2
        if mine:
            g.append(f'<circle cx="{ax - 4}" cy="{by + bh - 10}" r="10" fill="{t["me"]}"/>'
                     f'<text x="{ax - 4}" y="{by + bh - 6}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">V</text>')
        else:
            g.append(f'<circle cx="{ax + 4}" cy="{by + bh - 10}" r="10" fill="{t["border"]}"/>'
                     f'<text x="{ax + 4}" y="{by + bh - 5}" text-anchor="middle" font-size="11">👀</text>')
        g.append("</g>")
        out.append("".join(g))

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    for th in THEMES:
        with open(f"{outdir}/chat-{th}.svg", "w") as f:
            f.write(build(th))
    print("ok")
