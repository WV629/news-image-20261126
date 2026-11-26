#!/usr/bin/env python3
"""Render the Thursday 26 November 2026 world-news poster, 1024x1024.

Champion layout (news-image-20261122/23 post-mortems): date masthead,
red headline strip, three hero stories with big flat illustrations on
the top half, a THE DAY IN NUMBERS panel, region pills, twelve mid
cards each with its own visual panel and credibility badge, twenty
one-line briefs in two columns, a world map with numbered pins, a
DATE CHECK box and a HOW SURE legend. 35 stories in all, every one
dated 26 Nov 2026 (happened or first reported that day) with its
source. Drawn in code with Pillow; no network; deterministic output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (24, 24, 24)
RED = (186, 16, 28)
NAVY = (18, 32, 60)
TEAL = (13, 110, 102)
GOLD = (176, 84, 8)
GREY = (104, 99, 88)
LINE = (208, 201, 186)
CARD = (255, 255, 255)
SKY = (178, 214, 235)
SAND = (238, 222, 188)

FONTS = [
    "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(bold, size, serif=False):
    cands = []
    if serif:
        cands = [FONTS[0], FONTS[3]]
    elif bold:
        cands = [FONTS[1], FONTS[4]]
    else:
        cands = [FONTS[2], FONTS[5]]
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(d, text, f, width, max_lines):
    """Greedy wrap; truncates with ... if it overflows max_lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        elif len(lines) < max_lines - 1:
            lines.append(cur)
            cur = w
        else:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(words) > sum(len(l.split()) for l in lines) and lines:
        last = lines[-1]
        while last and d.textlength(last + " ...", font=f) > width:
            last = last.rsplit(" ", 1)[0] if " " in last else ""
        lines[-1] = (last + " ...") if last else "..."
    return lines


def badge(d, x, y, label):
    """Small credibility badge; returns width used."""
    cols = {"CONFIRMED": (18, 110, 60), "OFFICIAL": (18, 60, 110),
            "REPORTED": (150, 110, 10), "CLAIM": (170, 60, 30)}
    c = cols[label]
    f = font(True, 10)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 15], radius=7, fill=c)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def pin(d, x, y, n):
    d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=RED, outline=(255, 255, 255), width=2)
    f = font(True, 10)
    t = str(n)
    d.text((x - d.textlength(t, font=f) / 2, y - 6), t, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------------ data
# region codes: NA North America, SA Latin America, EU Europe,
# ME Middle East, AF Africa, SAS South Asia, EA East Asia,
# SEA Southeast Asia, OC Oceania

HEROES = [
    dict(n=1, place="NEW YORK", region="NA", badge="CONFIRMED",
         src="CNN / Reuters",
         head="MACY'S 100TH PARADE POSTPONED",
         body="First weather postponement in 100 years. Parade moves to Saturday, 8:30am ET.",
         art="balloon", big="100th"),
    dict(n=2, place="CAIRO", region="AF", badge="CONFIRMED",
         src="AP / CNN",
         head="CAIRO TANKER FIRE KILLS 31",
         body="Fuel tanker overturns on the Ring Road at Warraq; 31 dead, "
              "21 hurt, 27 vehicles charred.",
         art="fire", big="31"),
    dict(n=3, place="WASHINGTON", region="NA", badge="OFFICIAL",
         src="Reuters / USTR",
         head="TRUMP'S NEW TARIFFS HIT 14 PARTNERS",
         body="New 20-40% tariffs proposed on China, EU, Japan, India and 10 more; Nasdaq dives 4%.",
         art="chart", big="14"),
]

NUMBERS = [
    ("100", "Macy's parade\npostponed"),
    ("31", "killed in the\nCairo tanker fire"),
    ("14", "trading partners\nface new tariffs"),
    ("40%", "top tariff rate\nproposed on China"),
    ("18", "years since the\n26/11 Mumbai attacks"),
    ("2", "tankers hit by mines\nin the Strait of Hormuz"),
]

CARDS = [
    dict(n=4, place="HORMUZ", region="ME", badge="REPORTED", src="Reuters",
         head="TANKERS HIT MINES IN HORMUZ",
         body="Two tankers hit mines, Iran says; reopen offer in 48 hours.",
         big="2", art="sea"),
    dict(n=5, place="RIYADH", region="ME", badge="CLAIM", src="Reuters",
         head="HOUTHIS CLAIM SAUDI STRIKE",
         body="Houthis claim Ras Tanura hit; Brent crude tops $94.",
         big="$94", art="oil"),
    dict(n=6, place="TIANGONG", region="EA", badge="CONFIRMED", src="Al Jazeera",
         head="PAKISTAN'S FIRST ASTRONAUT",
         body="Zeeshan Ali, first foreigner aboard China's Tiangong.",
         big="1st", art="space"),
    dict(n=7, place="MUMBAI", region="SAS", badge="CONFIRMED", src="AIR News",
         head="MUMBAI: 18 YEARS SINCE 26/11",
         body="Memorials for the 166 killed in 2008; Rana trial moves on.",
         big="166", art="memorial"),
    dict(n=8, place="GENEVA", region="EU", badge="CONFIRMED", src="Times of India",
         head="CHESS: GAME 3 TODAY, 1-1",
         body="Gukesh, Sindarov drew twice in 20 moves. Both players are 20.",
         big="1-1", art="chess"),
    dict(n=9, place="PYONGYANG", region="EA", badge="OFFICIAL", src="AFP",
         head="KIM: MORE TACTICAL NUKES",
         body="Kim calls for wider deployment of tactical nuclear weapons.",
         big="KIM", art="missile"),
    dict(n=10, place="LONDON", region="EU", badge="CONFIRMED", src="NST",
         head="ANDY TAYLOR DIES AT 65",
         body="The guitarist dies after a battle with prostate cancer.",
         big="65", art="guitar"),
    dict(n=11, place="US COAST", region="NA", badge="CONFIRMED", src="AP",
         head="SIX DEAD IN US PLANE CRASH",
         body="A small plane goes down off the southern US coast; six dead.",
         big="6", art="plane"),
    dict(n=12, place="PRETORIA", region="AF", badge="CONFIRMED", src="Qatar Tribune",
         head="RAMAPHOSA REPORT UNLAWFUL",
         body="Court rules impeachment report against president unlawful.",
         big="COURT", art="court"),
    dict(n=13, place="HAVANA", region="SA", badge="OFFICIAL", src="Qatar Tribune",
         head="WHO: END CUBA FUEL BLOCKADE",
         body="WHO chief urges an end to the US fuel blockade on Cuba.",
         big="WHO", art="aid"),
    dict(n=14, place="KYIV", region="EU", badge="CLAIM", src="Reuters",
         head="UKRAINE: WE HIT AIR BASE",
         body="Kyiv says it struck a Russian air base, damaging five planes.",
         big="5", art="jet"),
    dict(n=15, place="BRUSSELS", region="EU", badge="OFFICIAL", src="Qatar Tribune",
         head="NATO BOOSTS EASTERN AIR WATCH",
         body="NATO steps up air surveillance on its eastern flank.",
         big="NATO", art="radar"),
]

BRIEFS = [
    ("Second US judge blocks Trump's birthright-citizenship order.", "Reuters", "NA"),
    ("Murmansk governor held in pre-trial detention in graft probe.", "Reuters", "EU"),
    ("Dozens of nations urge Russia to halt alleged riot-agent use.", "Reuters", "EU"),
    ("Kenyan cult leader, serving 200 years, convicted on new charges.", "Reuters", "AF"),
    ("Ecuador minister: US talks focus on reviewing operations.", "Reuters", "SA"),
    ("Lebanon to open a second international airport next month.", "Reuters", "ME"),
    ("Record ~2,000 migrants reach Spain's Canary Islands in one day.", "AP", "EU"),
    ("Bangladesh garment workers win a 36% pay rise.", "Manila Times", "SAS"),
    ("Kuala Lumpur sues Google for $146M over bad content.", "Manila Times", "SEA"),
    ("China probes Politburo member Chen Jining.", "Manila Times", "EA"),
    ("North Korea expels the head of the Swiss diplomatic office.", "AFP", "EA"),
    ("Colombian forces storm a supermarket and free hostages.", "AFP", "SA"),
    ("China and Cambodia stage joint military drills.", "AFP", "SEA"),
    ("Australia, Solomon Islands sign pact seen as counter to China.", "AFP", "OC"),
    ("Vance serves troops Thanksgiving meals; Giuliani honoured.", "ET", "NA"),
    ("Gold below $3,500, near one-year low; Bitcoin under $60,000.", "NST / ET", "NA"),
    ("Taiwan shares plunge 1,927 points; NT dollar past 33.", "SimpleLife", "EA"),
    ("Fed Beige Book: modest growth, stubborn price pressure.", "SimpleLife", "NA"),
    ("Australia backs big fines for big tech.", "NST", "OC"),
    ("PSG held 2-2 by Roma; Liverpool win 3-0 at Brugge.", "NST", "EU"),
]

REGIONS = [("NORTH AMERICA", "NA"), ("EUROPE", "EU"), ("MIDDLE EAST", "ME"),
           ("AFRICA", "AF"), ("SOUTH ASIA", "SAS"), ("EAST ASIA", "EA"),
           ("SOUTHEAST ASIA", "SEA"), ("LATIN AMERICA", "SA"), ("OCEANIA", "OC")]

DATECHECK = [
    ("Nvidia reinstates Jensen Huang; shares +31.5%", "Mon 23 Nov"),
    ("COP31 climate talks collapse", "Sun 22 Nov"),
    ("First tankers hit by mines in Hormuz", "Tue 24 Nov"),
    ("Anthropic lists on Nasdaq (ANT)", "Wed 19 Nov"),
    ("US PCE inflation report released", "Wed 25 Nov"),
]

# map pin positions (x, y) in the map box, keyed by story number
PINS = {1: (108, 42), 2: (322, 66), 3: (388, 58), 4: (398, 50), 5: (366, 74),
        6: (452, 62), 7: (428, 78), 8: (296, 40), 9: (492, 38), 10: (288, 26),
        11: (146, 84), 12: (318, 122), 13: (118, 64), 14: (340, 30),
        15: (306, 18)}


# ------------------------------------------------------------------ art
def draw_art(d, box, kind, big, col):
    """Flat illustration panel for a hero card."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "balloon":
        d.ellipse([cx - 52, y0 + 8, cx + 52, y0 + 78], fill=(235, 120, 40))
        d.ellipse([cx - 52, y0 + 8, cx - 8, y0 + 78], fill=(245, 170, 60))
        d.polygon([(cx - 8, y0 + 76), (cx + 8, y0 + 76), (cx, y0 + 92)], fill=(120, 60, 20))
        d.line([cx, y0 + 92, cx, y1 - 6], fill=(120, 60, 20), width=2)
        d.ellipse([x0 + 14, y0 + 58, x0 + 46, y0 + 90], fill=(255, 255, 255))
        d.ellipse([x1 - 46, y0 + 20, x1 - 14, y0 + 52], fill=(255, 255, 255))
    elif kind == "fire":
        d.polygon([(x0 + 30, y1 - 8), (x0 + 90, y1 - 8), (x0 + 60, y0 + 30)], fill=(60, 60, 60))
        d.polygon([(cx + 10, y1 - 8), (cx + 70, y1 - 8), (cx + 40, y0 + 44)], fill=(40, 40, 40))
        d.ellipse([cx - 34, y0 + 34, cx + 34, y0 + 96], fill=(240, 90, 20))
        d.ellipse([cx - 18, y0 + 52, cx + 18, y0 + 96], fill=(250, 190, 40))
        d.ellipse([cx - 8, y0 + 70, cx + 8, y0 + 96], fill=(255, 240, 120))
        for xx in (x0 + 18, x1 - 60):
            d.rectangle([xx, y0 + 12, xx + 42, y0 + 22], fill=(90, 90, 90))
    elif kind == "chart":
        d.line([x0 + 16, y0 + 18, x0 + 70, y0 + 40, x0 + 120, y0 + 30,
                x0 + 170, y0 + 58, x0 + 220, y0 + 52, x0 + 280, y0 + 86],
               fill=(255, 255, 255), width=5)
        d.polygon([(x0 + 280, y0 + 86), (x0 + 292, y0 + 86), (x0 + 280, y0 + 98)],
                  fill=(255, 255, 255))
        for xx in (x0 + 40, x0 + 110, x0 + 180, x0 + 250):
            d.rectangle([xx, y1 - 26, xx + 22, y1 - 10], fill=(255, 255, 255, 90))
    f = font(True, 30)
    by_ = y0 + 6 if kind == "chart" else y1 - 40
    d.text((x1 - d.textlength(big, font=f) - 10, by_), big, font=f,
           fill=(255, 255, 255))


def draw_card_art(d, box, kind, big, col):
    """Small visual panel: big word/number over a flat motif."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    cx = (x0 + x1) // 2
    if kind in ("sea", "oil"):
        for i, yy in enumerate((y0 + 10, y0 + 20, y0 + 30)):
            d.arc([x0 + 6, yy - 6, x1 - 6, yy + 10], 0, 180, fill=(255, 255, 255), width=2)
        d.polygon([(cx - 26, y0 + 8), (cx + 26, y0 + 8), (cx, y0 + 26)], fill=(255, 255, 255))
    elif kind == "space":
        d.ellipse([cx - 12, y0 + 6, cx + 12, y0 + 30], fill=(255, 255, 255))
        d.rectangle([cx - 26, y0 + 18, cx + 26, y0 + 26], fill=(255, 255, 255))
        for px, py in ((x0 + 12, y0 + 8), (x1 - 16, y0 + 12), (x0 + 20, y0 + 26)):
            d.ellipse([px, py, px + 3, py + 3], fill=(255, 255, 255))
    elif kind == "chess":
        for i in range(4):
            for j in range(2):
                if (i + j) % 2 == 0:
                    d.rectangle([x0 + 8 + i * 14, y0 + 6 + j * 14,
                                 x0 + 22 + i * 14, y0 + 20 + j * 14],
                                fill=(255, 255, 255))
        d.ellipse([cx + 14, y0 + 8, cx + 30, y0 + 24], fill=(255, 255, 255))
    elif kind == "missile":
        d.polygon([(cx - 4, y0 + 4), (cx + 4, y0 + 4), (cx, y0 + 18)], fill=(255, 255, 255))
        d.rectangle([cx - 4, y0 + 18, cx + 4, y0 + 32], fill=(255, 255, 255))
    elif kind == "guitar":
        d.ellipse([cx - 12, y0 + 12, cx + 12, y0 + 34], fill=(255, 255, 255))
        d.rectangle([cx - 3, y0 + 2, cx + 3, y0 + 16], fill=(255, 255, 255))
    elif kind == "plane":
        d.polygon([(x0 + 10, y0 + 18), (x1 - 10, y0 + 14), (x1 - 30, y0 + 24),
                   (x0 + 30, y0 + 26)], fill=(255, 255, 255))
    elif kind == "court":
        for xx in (x0 + 14, cx - 2, x1 - 26):
            d.rectangle([xx, y0 + 10, xx + 10, y0 + 30], fill=(255, 255, 255))
        d.rectangle([x0 + 8, y0 + 30, x1 - 8, y0 + 34], fill=(255, 255, 255))
    elif kind == "aid":
        d.rectangle([cx - 12, y0 + 6, cx - 4, y0 + 32], fill=(255, 255, 255))
        d.rectangle([cx - 18, y0 + 14, cx + 2, y0 + 22], fill=(255, 255, 255))
    elif kind in ("jet", "radar"):
        d.polygon([(x0 + 12, y0 + 20), (x1 - 12, y0 + 12), (x1 - 12, y0 + 26),
                   (x0 + 12, y0 + 26)], fill=(255, 255, 255))
        d.ellipse([cx - 3, y0 + 6, cx + 3, y0 + 12], fill=(255, 255, 255))
    elif kind == "memorial":
        d.ellipse([cx - 14, y0 + 8, cx + 14, y0 + 34], fill=(255, 255, 255))
        d.rectangle([cx - 2, y0 + 20, cx + 2, y0 + 34], fill=(255, 255, 255))
    size = 26
    while size > 12 and d.textlength(big, font=font(True, size)) > (x1 - x0) - 12:
        size -= 2
    f = font(True, size)
    tw = d.textlength(big, font=f)
    d.text((x1 - tw - 6, y1 - size - 6), big, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------------ render
def render():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    mx = 24
    # masthead
    d.text((mx, 14), "THURSDAY 26 NOVEMBER 2026", font=font(True, 40, serif=True), fill=INK)
    d.text((mx, 60), "THE WORLD IN ONE PAGE  ·  35 dated stories  ·  9 regions",
           font=font(True, 15), fill=GREY)
    d.text((W - mx - 150, 22), "ONE DAY.", font=font(True, 26, serif=True), fill=RED)
    d.text((W - mx - 150, 52), "EVERY REGION.", font=font(True, 15), fill=INK)
    d.line([mx, 84, W - mx, 84], fill=INK, width=2)
    # red headline strip
    d.rectangle([mx, 90, W - mx, 116], fill=RED)
    strip = ("1  MACY'S 100TH PARADE POSTPONED   •   2  CAIRO FIRE KILLS 31   •   "
             "3  TRUMP TARIFFS HIT 14 PARTNERS")
    d.text((mx + 10, 97), strip, font=font(True, 15), fill=(255, 255, 255))
    # heroes
    hy, hh = 124, 216
    hw = (W - 2 * mx - 2 * 12) // 3
    cols = [(NAVY, (200, 220, 235)), (TEAL, (205, 225, 215)), (GOLD, (240, 220, 190))]
    for i, h in enumerate(HEROES):
        x0 = mx + i * (hw + 12)
        x1 = x0 + hw
        d.rounded_rectangle([x0, hy, x1, hy + hh], radius=8, fill=CARD, outline=LINE, width=1)
        draw_art(d, (x0 + 1, hy + 1, x1 - 1, hy + 96), h["art"], h["big"], cols[i][0])
        pin(d, x0 + 16, hy + 16, h["n"])
        d.text((x0 + 10, hy + 104), h["place"], font=font(True, 11), fill=RED)
        for j, ln in enumerate(wrap(d, h["head"], font(True, 17), hw - 20, 2)):
            d.text((x0 + 10, hy + 120 + j * 20), ln, font=font(True, 17), fill=INK)
        for j, ln in enumerate(wrap(d, h["body"], font(False, 12.5), hw - 20, 2)):
            d.text((x0 + 10, hy + 162 + j * 15), ln, font=font(False, 12.5), fill=(60, 58, 52))
        d.text((x0 + 10, hy + hh - 16), h["src"], font=font(False, 10), fill=GREY)
        badge(d, x1 - 78, hy + hh - 18, h["badge"])
    # numbers panel
    ny = 348
    d.rectangle([mx, ny, W - mx, ny + 52], fill=NAVY)
    d.text((mx + 12, ny + 8), "THE DAY\nIN NUMBERS", font=font(True, 12), fill=(255, 255, 255))
    seg = (W - 2 * mx - 150) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = mx + 150 + i * seg
        d.text((x, ny + 4), num, font=font(True, 24), fill=(255, 210, 90))
        for j, ln in enumerate(cap.split("\n")):
            d.text((x, ny + 30 + j * 11), ln, font=font(False, 9.5), fill=(220, 225, 235))
        if i:
            d.line([x - 8, ny + 8, x - 8, ny + 44], fill=(90, 105, 130), width=1)
    # region pills
    counts = {}
    for s in HEROES + CARDS:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    for _, _, r in BRIEFS:
        counts[r] = counts.get(r, 0) + 1
    px = mx
    py = 408
    for name, code in REGIONS:
        label = f"{name} {counts.get(code, 0)}"
        f = font(True, 11)
        w = d.textlength(label, font=f) + 16
        d.rounded_rectangle([px, py, px + w, py + 20], radius=10,
                            fill=(255, 255, 255), outline=LINE, width=1)
        d.text((px + 8, py + 4), label, font=f, fill=INK)
        px += w + 7
    # mid cards: 4 cols x 3 rows
    gy, gh = 436, 76
    cw = (W - 2 * mx - 3 * 10) // 4
    card_cols = [NAVY, TEAL, GOLD, (120, 40, 90), (40, 90, 120), (90, 90, 40),
                 (150, 60, 20), (30, 90, 60), (100, 30, 60), (60, 60, 120),
                 (140, 100, 10), (20, 80, 100)]
    for i, c in enumerate(CARDS):
        r, col = divmod(i, 4)
        x0 = mx + col * (cw + 10)
        y0 = gy + r * (gh + 8)
        x1, y1 = x0 + cw, y0 + gh
        d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD, outline=LINE, width=1)
        draw_card_art(d, (x0 + 1, y0 + 1, x0 + 64, y1 - 1), c["art"], c["big"], card_cols[i])
        pin(d, x0 + 11, y0 + 11, c["n"])
        tx = x0 + 70
        for j, ln in enumerate(wrap(d, c["head"], font(True, 11.5), cw - 76, 2)):
            d.text((tx, y0 + 5 + j * 14), ln, font=font(True, 11.5), fill=INK)
        for j, ln in enumerate(wrap(d, c["body"], font(False, 10.5), cw - 76, 2)):
            d.text((tx, y0 + 34 + j * 12), ln, font=font(False, 10.5), fill=(60, 58, 52))
        d.text((tx, y1 - 13), c["src"], font=font(False, 9), fill=GREY)
        badge(d, x1 - 62, y1 - 14, c["badge"])
    # briefs
    by = 694
    d.text((mx, by), "THE REST OF THE DAY — 20 MORE STORIES",
           font=font(True, 14), fill=RED)
    d.line([mx, by + 20, W - mx, by + 20], fill=LINE, width=1)
    bf = font(False, 13)
    row_h = 17
    half = 10
    colw = (W - 2 * mx) // 2
    for i, (txt, src, _) in enumerate(BRIEFS):
        col, row = divmod(i, half)
        x = mx if col == 0 else mx + colw + 8
        y = by + 26 + row * row_h
        d.text((x, y), f"{16 + i}.", font=font(True, 12), fill=RED)
        srcw = d.textlength(src, font=font(False, 9))
        avail = colw - 26 - srcw - 14
        t = txt
        while t and d.textlength(t + " ...", font=bf) > avail:
            t = t.rsplit(" ", 1)[0] if " " in t else ""
        if t != txt:
            t = t + " ..."
        d.text((x + 26, y), t, font=bf, fill=INK)
        d.text((x + colw - 8 - srcw, y + 1), src, font=font(False, 9), fill=GREY)
    # bottom band: map + date check + legend
    ty = 890
    d.line([mx, ty - 6, W - mx, ty - 6], fill=LINE, width=1)
    # map
    mapx, mapy, mapw, maph = mx, ty, 560, 110
    d.rounded_rectangle([mapx, mapy, mapx + mapw, mapy + maph], radius=6,
                        fill=(205, 225, 238), outline=LINE, width=1)
    d.text((mapx + 8, mapy + 4), "WHERE IT HAPPENED", font=font(True, 11), fill=NAVY)
    land = (150, 175, 140)
    # rough continents
    d.polygon([(mapx + 30, mapy + 34), (mapx + 150, mapy + 26), (mapx + 165, mapy + 52),
               (mapx + 120, mapy + 74), (mapx + 60, mapy + 72), (mapx + 28, mapy + 52)], fill=land)
    d.polygon([(mapx + 150, mapy + 78), (mapx + 190, mapy + 76), (mapx + 200, mapy + 104),
               (mapx + 175, mapy + 112), (mapx + 152, mapy + 92)], fill=land)
    d.polygon([(mapx + 265, mapy + 26), (mapx + 320, mapy + 22), (mapx + 330, mapy + 48),
               (mapx + 300, mapy + 56), (mapx + 268, mapy + 48)], fill=land)
    d.polygon([(mapx + 285, mapy + 58), (mapx + 335, mapy + 56), (mapx + 345, mapy + 92),
               (mapx + 320, mapy + 108), (mapx + 292, mapy + 86)], fill=land)
    d.polygon([(mapx + 335, mapy + 24), (mapx + 510, mapy + 20), (mapx + 530, mapy + 48),
               (mapx + 480, mapy + 70), (mapx + 400, mapy + 66), (mapx + 345, mapy + 50)], fill=land)
    d.ellipse([mapx + 470, mapy + 76, mapx + 500, mapy + 88], fill=land)
    d.ellipse([mapx + 505, mapy + 88, mapx + 545, mapy + 102], fill=land)
    for n, (px_, py_) in PINS.items():
        pin(d, mapx + px_, mapy + py_, n)
    # UTC strip inside map bottom
    d.text((mapx + 8, mapy + maph - 14), "UTC  00:00 ——— 06:00 ——— 12:00 ——— 18:00 ——— 24:00   ·   "
           "Game 3 in Geneva 14:00 UTC", font=font(False, 9), fill=NAVY)
    # date check
    dx = mapx + mapw + 12
    dw = W - mx - dx
    d.rounded_rectangle([dx, ty, dx + dw, ty + 72], radius=6, fill=(255, 248, 230),
                        outline=(220, 190, 120), width=1)
    d.text((dx + 8, ty + 5), "DATE CHECK — LEFT OUT ON PURPOSE", font=font(True, 11), fill=GOLD)
    for i, (item, when) in enumerate(DATECHECK):
        y = ty + 22 + i * 10
        if y > ty + 68:
            break
        whenw = d.textlength(when, font=font(True, 9))
        it = item
        f9 = font(False, 9.5)
        while it and d.textlength("x " + it, font=f9) > dw - 16 - whenw - 8:
            it = it.rsplit(" ", 1)[0] if " " in it else ""
        d.text((dx + 8, y), "x " + it, font=f9, fill=(90, 80, 60))
        d.text((dx + dw - 8 - whenw, y), when, font=font(True, 9), fill=GOLD)
    # how sure legend
    ly = ty + 80
    d.rounded_rectangle([dx, ly, dx + dw, ly + 36], radius=6, fill=CARD, outline=LINE, width=1)
    d.text((dx + 8, ly + 4), "HOW SURE", font=font(True, 11), fill=INK)
    d.text((dx + 82, ly + 6), "verified · announced · sourced · alleged",
           font=font(False, 9), fill=GREY)
    lx = dx + 8
    for label in ("CONFIRMED", "OFFICIAL", "REPORTED", "CLAIM"):
        lx += badge(d, lx, ly + 19, label) + 8
    d.text((mx, H - 16), "Sources: Reuters · AP · CNN · AFP · Al Jazeera · Times of India · "
           "Qatar Tribune · NST · Manila Times · AIR News · SimpleLife · ET — "
           "all stories dated 26 Nov 2026.", font=font(False, 9), fill=GREY)
    return im


if __name__ == "__main__":
    out = os.environ.get("OUT", "entry.png")
    im = render()
    im.save(out, optimize=True)
    print(out, im.size, os.path.getsize(out), "bytes")
