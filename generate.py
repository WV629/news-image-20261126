#!/usr/bin/env python3
"""Render the Thursday 26 November 2026 world-news poster, 1024x1024.

Champion layout (news-image-20261122/23 post-mortems, checked against the
23 Nov winner): date masthead, red headline strip, a UTC timeline, three
hero stories with big flat illustrations on the top half, a THE DAY IN
NUMBERS panel, region pills, ten mid cards in two rows of five, each with
its own large visual panel and credibility badge, twenty-two one-line
briefs beside a world map with numbered pins, a DATE CHECK strip and a
HOW SURE legend. 35 stories in all, every one dated 26 Nov 2026
(happened or first reported that day) with its source. Drawn in code
with Pillow; no network; deterministic output.
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
         body="Fuel tanker overturns on the Ring Road at Warraq; 31 dead, 21 hurt, 27 vehicles charred.",
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
         body="Two tankers hit mines, Iran says; reopen in 48 hours.",
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
         body="Memorials for 166 killed in 2008; Rana trial goes on.",
         big="166", art="memorial"),
    dict(n=8, place="GENEVA", region="EU", badge="CONFIRMED", src="Times of India",
         head="CHESS: GAME 3 TODAY, 1-1",
         body="Gukesh, Sindarov drew twice in 20 moves; both are 20.",
         big="1-1", art="chess"),
    dict(n=9, place="PYONGYANG", region="EA", badge="OFFICIAL", src="AFP",
         head="KIM: MORE TACTICAL NUKES",
         body="Kim calls for more tactical nuclear weapons.",
         big="KIM", art="missile"),
    dict(n=10, place="LONDON", region="EU", badge="CONFIRMED", src="NST",
         head="ANDY TAYLOR DIES AT 65",
         body="The guitarist dies after a battle with prostate cancer.",
         big="65", art="guitar"),
    dict(n=11, place="HAVANA", region="SA", badge="OFFICIAL", src="Qatar Tribune",
         head="WHO: END CUBA FUEL BLOCKADE",
         body="WHO chief urges an end to the US fuel blockade on Cuba.",
         big="WHO", art="aid"),
    dict(n=12, place="KYIV", region="EU", badge="CLAIM", src="Reuters",
         head="UKRAINE: WE HIT AIR BASE",
         body="Kyiv says it hit a Russian air base, five planes damaged.",
         big="5", art="jet"),
    dict(n=13, place="BRUSSELS", region="EU", badge="OFFICIAL", src="Qatar Tribune",
         head="NATO BOOSTS EASTERN AIR WATCH",
         body="NATO steps up air surveillance on its eastern flank.",
         big="NATO", art="radar"),
]

BRIEFS = [
    ("Second judge blocks birthright order.", "Reuters", "NA"),
    ("Murmansk governor held in graft probe.", "Reuters", "EU"),
    ("States urge Russia to halt riot-agent.", "Reuters", "EU"),
    ("Kenyan cult leader convicted again.", "Reuters", "AF"),
    ("Ecuador: US talks review operations.", "Reuters", "SA"),
    ("Lebanon to open a second airport.", "Reuters", "ME"),
    ("Record 2,000 migrants reach Canaries.", "AP", "EU"),
    ("Bangladesh garment pay rise of 36%.", "Manila Times", "SAS"),
    ("Kuala Lumpur sues Google for $146M.", "Manila Times", "SEA"),
    ("China probes Politburo's Chen Jining.", "Manila Times", "EA"),
    ("North Korea expels Swiss office head.", "AFP", "EA"),
    ("Colombia frees supermarket hostages.", "AFP", "SA"),
    ("China, Cambodia hold joint drills.", "AFP", "SEA"),
    ("Australia-Solomons pact counters China.", "AFP", "OC"),
    ("Vance serves troops Thanksgiving meals.", "ET", "NA"),
    ("Gold <$3,500; Bitcoin <$60,000.", "NST / ET", "NA"),
    ("Taiwan shares plunge 1,927 points.", "SimpleLife", "EA"),
    ("Fed: modest growth, stubborn prices.", "SimpleLife", "NA"),
    ("Australia backs big fines for big tech.", "NST", "OC"),
    ("PSG 2-2 Roma; Liverpool win 3-0.", "NST", "EU"),
    ("Six dead in plane crash off US coast.", "AP", "NA"),
    ("Court: Ramaphosa report unlawful.", "Qatar Tribune", "AF"),
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

# map pin positions (x, y) in the small map box, keyed by story number
PINS = {1: (58, 28), 2: (168, 54), 3: (78, 42), 4: (190, 36), 5: (212, 48),
        6: (240, 30), 7: (228, 60), 8: (164, 34), 9: (256, 44), 10: (150, 22),
        11: (96, 62), 12: (188, 30), 13: (176, 14)}


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
    """Large visual panel for a mid card: motif plus a big word/number."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    cx = (x0 + x1) // 2
    if kind in ("sea", "oil"):
        for yy in (y0 + 22, y0 + 38, y0 + 54):
            d.arc([x0 + 14, yy - 10, x1 - 14, yy + 16], 0, 180, fill=(255, 255, 255), width=3)
        d.polygon([(cx - 34, y0 + 10), (cx + 34, y0 + 10), (cx, y0 + 34)], fill=(255, 255, 255))
    elif kind == "space":
        d.ellipse([cx - 16, y0 + 10, cx + 16, y0 + 42], fill=(255, 255, 255))
        d.rectangle([cx - 34, y0 + 26, cx + 34, y0 + 36], fill=(255, 255, 255))
        for px, py in ((x0 + 16, y0 + 12), (x1 - 20, y0 + 16), (x0 + 26, y0 + 40)):
            d.ellipse([px, py, px + 4, py + 4], fill=(255, 255, 255))
    elif kind == "chess":
        for i in range(5):
            for j in range(3):
                if (i + j) % 2 == 0:
                    d.rectangle([x0 + 12 + i * 16, y0 + 10 + j * 16,
                                 x0 + 28 + i * 16, y0 + 26 + j * 16],
                                fill=(255, 255, 255))
        d.ellipse([cx + 20, y0 + 12, cx + 40, y0 + 32], fill=(255, 255, 255))
    elif kind == "missile":
        d.polygon([(cx - 6, y0 + 6), (cx + 6, y0 + 6), (cx, y0 + 26)], fill=(255, 255, 255))
        d.rectangle([cx - 6, y0 + 26, cx + 6, y0 + 48], fill=(255, 255, 255))
    elif kind == "guitar":
        d.ellipse([cx - 16, y0 + 16, cx + 16, y0 + 48], fill=(255, 255, 255))
        d.rectangle([cx - 4, y0 + 4, cx + 4, y0 + 22], fill=(255, 255, 255))
    elif kind == "court":
        for xx in (x0 + 18, cx - 4, x1 - 34):
            d.rectangle([xx, y0 + 14, xx + 14, y0 + 44], fill=(255, 255, 255))
        d.rectangle([x0 + 10, y0 + 44, x1 - 10, y0 + 50], fill=(255, 255, 255))
    elif kind == "aid":
        d.rectangle([cx - 16, y0 + 10, cx - 4, y0 + 48], fill=(255, 255, 255))
        d.rectangle([cx - 24, y0 + 22, cx + 4, y0 + 34], fill=(255, 255, 255))
    elif kind in ("jet", "radar"):
        d.polygon([(x0 + 16, y0 + 30), (x1 - 16, y0 + 18), (x1 - 16, y0 + 40),
                   (x0 + 16, y0 + 40)], fill=(255, 255, 255))
        d.ellipse([cx - 4, y0 + 10, cx + 4, y0 + 18], fill=(255, 255, 255))
    elif kind == "memorial":
        d.ellipse([cx - 18, y0 + 12, cx + 18, y0 + 50], fill=(255, 255, 255))
        d.rectangle([cx - 3, y0 + 30, cx + 3, y0 + 50], fill=(255, 255, 255))
    size = 30
    while size > 14 and d.textlength(big, font=font(True, size)) > (x1 - x0) - 16:
        size -= 2
    f = font(True, size)
    tw = d.textlength(big, font=f)
    d.text((x1 - tw - 8, y1 - size - 8), big, font=f, fill=(255, 255, 255))


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
    d.rectangle([mx, 90, W - mx, 114], fill=RED)
    strip = ("1  MACY'S 100TH PARADE POSTPONED   •   2  CAIRO FIRE KILLS 31   •   "
             "3  TRUMP TARIFFS HIT 14 PARTNERS")
    d.text((mx + 10, 97), strip, font=font(True, 15), fill=(255, 255, 255))
    # UTC timeline
    d.text((mx, 120), "THURSDAY UTC", font=font(True, 11), fill=RED)
    d.line([mx + 108, 128, W - mx, 128], fill=LINE, width=2)
    marks = [("00:00", "Asia wakes"), ("06:00", "Europe opens"),
             ("12:00", "Americas wake"), ("14:00", "Game 3, Geneva"),
             ("18:00", "Thanksgiving, New York"), ("24:00", "Day ends")]
    seg = (W - 2 * mx - 108) / 5
    for i, (t, label) in enumerate(marks):
        x = mx + 108 + i * seg
        d.ellipse([x - 3, 125, x + 3, 131], fill=RED)
        tw = d.textlength(t, font=font(True, 9))
        tx = min(max(x - tw / 2, mx + 108), W - mx - tw)
        d.text((tx, 114), t, font=font(True, 9), fill=INK)
        lw = d.textlength(label, font=font(False, 9))
        lx = min(max(x - lw / 2, mx + 108), W - mx - lw)
        d.text((lx, 132), label, font=font(False, 9), fill=GREY)
    # heroes
    hy, hh = 142, 194
    hw = (W - 2 * mx - 2 * 12) // 3
    cols = [(NAVY, (200, 220, 235)), (TEAL, (205, 225, 215)), (GOLD, (240, 220, 190))]
    for i, h in enumerate(HEROES):
        x0 = mx + i * (hw + 12)
        x1 = x0 + hw
        d.rounded_rectangle([x0, hy, x1, hy + hh], radius=8, fill=CARD, outline=LINE, width=1)
        draw_art(d, (x0 + 1, hy + 1, x1 - 1, hy + 84), h["art"], h["big"], cols[i][0])
        pin(d, x0 + 16, hy + 16, h["n"])
        d.text((x0 + 10, hy + 90), h["place"], font=font(True, 11), fill=RED)
        for j, ln in enumerate(wrap(d, h["head"], font(True, 17), hw - 20, 2)):
            d.text((x0 + 10, hy + 104 + j * 20), ln, font=font(True, 17), fill=INK)
        for j, ln in enumerate(wrap(d, h["body"], font(False, 12.5), hw - 20, 2)):
            d.text((x0 + 10, hy + 142 + j * 15), ln, font=font(False, 12.5), fill=(60, 58, 52))
        d.text((x0 + 10, hy + hh - 16), h["src"], font=font(False, 10), fill=GREY)
        badge(d, x1 - 78, hy + hh - 18, h["badge"])
    # numbers panel
    ny = 344
    d.rectangle([mx, ny, W - mx, ny + 48], fill=NAVY)
    d.text((mx + 12, ny + 7), "THE DAY\nIN NUMBERS", font=font(True, 12), fill=(255, 255, 255))
    seg = (W - 2 * mx - 150) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = mx + 150 + i * seg
        d.text((x, ny + 2), num, font=font(True, 24), fill=(255, 210, 90))
        for j, ln in enumerate(cap.split("\n")):
            d.text((x, ny + 27 + j * 10), ln, font=font(False, 9.5), fill=(220, 225, 235))
        if i:
            d.line([x - 8, ny + 7, x - 8, ny + 41], fill=(90, 105, 130), width=1)
    # region pills
    counts = {}
    for s in HEROES + CARDS:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    for _, _, r in BRIEFS:
        counts[r] = counts.get(r, 0) + 1
    px = mx
    py = 400
    for name, code in REGIONS:
        label = f"{name} {counts.get(code, 0)}"
        f = font(True, 11)
        w = d.textlength(label, font=f) + 16
        d.rounded_rectangle([px, py, px + w, py + 20], radius=10,
                            fill=(255, 255, 255), outline=LINE, width=1)
        d.text((px + 8, py + 4), label, font=f, fill=INK)
        px += w + 7
    # mid cards: 2 rows of 5, each with a large visual panel
    gy, gh = 428, 171
    cw = (W - 2 * mx - 4 * 10) // 5
    card_cols = [NAVY, TEAL, GOLD, (120, 40, 90), (40, 90, 120), (90, 90, 40),
                 (150, 60, 20), (30, 90, 60), (100, 30, 60), (60, 60, 120)]
    for i, c in enumerate(CARDS):
        r, col = divmod(i, 5)
        x0 = mx + col * (cw + 10)
        y0 = gy + r * (gh + 8)
        x1, y1 = x0 + cw, y0 + gh
        d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD, outline=LINE, width=1)
        draw_card_art(d, (x0 + 1, y0 + 1, x1 - 1, y0 + 84), c["art"], c["big"], card_cols[i])
        pin(d, x0 + 13, y0 + 13, c["n"])
        for j, ln in enumerate(wrap(d, c["head"], font(True, 11.5), cw - 16, 2)):
            d.text((x0 + 8, y0 + 90 + j * 14), ln, font=font(True, 11.5), fill=INK)
        for j, ln in enumerate(wrap(d, c["body"], font(False, 10), cw - 16, 2)):
            d.text((x0 + 8, y0 + 120 + j * 12), ln, font=font(False, 10), fill=(60, 58, 52))
        d.text((x0 + 8, y1 - 13), c["src"], font=font(False, 9), fill=GREY)
        badge(d, x1 - 80, y1 - 14, c["badge"])
    # bottom band: map + date check on the left, briefs on the right
    by = 786
    d.text((mx, by), "WHERE IT HAPPENED", font=font(True, 12), fill=NAVY)
    mapx, mapy, mapw, maph = mx, by + 20, 306, 124
    d.rounded_rectangle([mapx, mapy, mapx + mapw, mapy + maph], radius=6,
                        fill=(205, 225, 238), outline=LINE, width=1)
    land = (150, 175, 140)
    d.polygon([(mapx + 16, mapy + 22), (mapx + 84, mapy + 16), (mapx + 92, mapy + 34),
               (mapx + 66, mapy + 48), (mapx + 32, mapy + 46), (mapx + 14, mapy + 34)], fill=land)
    d.polygon([(mapx + 82, mapy + 52), (mapx + 104, mapy + 50), (mapx + 110, mapy + 68),
               (mapx + 96, mapy + 74), (mapx + 84, mapy + 62)], fill=land)
    d.polygon([(mapx + 146, mapy + 16), (mapx + 176, mapy + 14), (mapx + 182, mapy + 32),
               (mapx + 164, mapy + 38), (mapx + 148, mapy + 32)], fill=land)
    d.polygon([(mapx + 156, mapy + 40), (mapx + 184, mapy + 38), (mapx + 190, mapy + 62),
               (mapx + 176, mapy + 72), (mapx + 160, mapy + 58)], fill=land)
    d.polygon([(mapx + 184, mapy + 14), (mapx + 280, mapy + 12), (mapx + 292, mapy + 32),
               (mapx + 264, mapy + 46), (mapx + 220, mapy + 44), (mapx + 190, mapy + 32)], fill=land)
    d.ellipse([mapx + 258, mapy + 50, mapx + 276, mapy + 58], fill=land)
    d.ellipse([mapx + 278, mapy + 58, mapx + 300, mapy + 68], fill=land)
    for n, (px_, py_) in PINS.items():
        pin(d, mapx + px_, mapy + py_, n)
    d.text((mapx + 8, mapy + maph - 14), "Pins 1-13: heroes and mid cards",
           font=font(False, 9), fill=NAVY)
    # date check box under the map
    dx = mx
    dw = mapw
    ty = mapy + maph + 8
    d.rounded_rectangle([dx, ty, dx + dw, ty + 66], radius=6, fill=(255, 248, 230),
                        outline=(220, 190, 120), width=1)
    d.text((dx + 8, ty + 4), "DATE CHECK — LEFT OUT ON PURPOSE", font=font(True, 10), fill=GOLD)
    for i, (item, when) in enumerate(DATECHECK):
        y = ty + 17 + i * 9
        whenw = d.textlength(when, font=font(True, 8.5))
        it = item
        f9 = font(False, 9)
        while it and d.textlength("x " + it, font=f9) > dw - 16 - whenw - 6:
            it = it.rsplit(" ", 1)[0] if " " in it else ""
        d.text((dx + 8, y), "x " + it, font=f9, fill=(90, 80, 60))
        d.text((dx + dw - 8 - whenw, y), when, font=font(True, 8.5), fill=GOLD)
    # briefs on the right
    bx = mapx + mapw + 12
    bw = W - mx - bx
    d.text((bx, by), "THE REST OF THE DAY — 22 MORE STORIES",
           font=font(True, 13), fill=RED)
    d.line([bx, by + 18, W - mx, by + 18], fill=LINE, width=1)
    bf = font(False, 12)
    colw = (bw - 8) // 2
    half = 11
    for i, (txt, src, _) in enumerate(BRIEFS):
        col, row = divmod(i, half)
        x = bx if col == 0 else bx + colw + 8
        y = by + 24 + row * 17
        d.text((x, y), f"{14 + i}.", font=font(True, 11), fill=RED)
        srcw = d.textlength(src, font=font(False, 8.5))
        avail = colw - 24 - srcw - 10
        t = txt
        while t and d.textlength(t + " ...", font=bf) > avail:
            t = t.rsplit(" ", 1)[0] if " " in t else ""
        if t != txt:
            t = t + " ..."
        d.text((x + 24, y), t, font=bf, fill=INK)
        d.text((x + colw - 8 - srcw, y + 1), src, font=font(False, 8.5), fill=GREY)
    # footer: how sure + sources on one line
    d.text((mx, H - 16), "HOW SURE: CONFIRMED verified · OFFICIAL announced · "
           "REPORTED sourced · CLAIM alleged  |  Reuters · AP · CNN · AFP · "
           "Al Jazeera · ToI · Qatar Tribune · NST · Manila Times · AIR News · "
           "SimpleLife · ET",
           font=font(False, 9), fill=GREY)
    return im


if __name__ == "__main__":
    out = os.environ.get("OUT", "entry.png")
    im = render()
    im.save(out, optimize=True)
    print(out, im.size, os.path.getsize(out), "bytes")
