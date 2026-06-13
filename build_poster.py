"""UK vs China: Top 5 Universities.

Two outputs:
  * gifs/...  - a slide-by-slide animation, ONE chart at a time (title,
                rise, head-to-head, internationalisation, size, takeaways).
  * charts/poster_static.png - the all-in-one overview poster.
Academic head-to-head theme: UK (Oxford) blue vs China (Tsinghua) crimson,
with a parchment-gold accent.
"""
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

# ------------------------------------------------------------- theme
BG = "#0C1322"
CARD = "#152033"
EDGE = "#27344F"
UKBLUE = "#5B9BFF"
CNRED = "#FF5252"
GOLD = "#E8B84B"
TEXT = "#ECF1FB"
MUTED = "#90A0BC"

plt.rcParams.update({
    "font.family": "Arial",
    "text.color": TEXT,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": EDGE,
})

W, H, DPI = 7.2, 10.8, 100  # 720 x 1080
ease = lambda t: t * t * (3 - 2 * t)

# ------------------------------------------------------------- data
uni = pd.read_csv("data/universities.csv")
hist = pd.read_csv("data/the_rank_history.csv").set_index("year")
uk = uni[uni.country == "UK"]
cn = uni[uni.country == "China"]
YEARS = hist.index.values


def avg(frame, col):
    return frame[col].mean()


VERSUS = [  # label, uk value, cn value, formatter, mode
    ("Avg world rank (QS 2026)", avg(uk, "qs2026_rank"), avg(cn, "qs2026_rank"),
     lambda v: f"#{v:.0f}", "ratio"),
    ("Avg students", avg(uk, "students_thousands"), avg(cn, "students_thousands"),
     lambda v: f"{v:.0f}k", "ratio"),
    ("Intl students", avg(uk, "intl_pct"), avg(cn, "intl_pct"),
     lambda v: f"{v:.0f}%", "ratio"),
    ("Avg founded", avg(uk, "founded"), avg(cn, "founded"),
     lambda v: f"{v:.0f}", "year"),
]
best_uk = uk.loc[uk.qs2026_rank.idxmin()]
best_cn = cn.loc[cn.qs2026_rank.idxmin()]
tsinghua_rise = hist["Tsinghua"].iloc[0] - hist["Tsinghua"].iloc[-1]
peking_rise = hist["Peking"].iloc[0] - hist["Peking"].iloc[-1]

SHORT = lambda n: n.replace(" College London", "").replace(
    "Shanghai Jiao Tong", "SJTU")


# ------------------------------------------------------------- helpers
def fig_to_frame(fig):
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()
    plt.close(fig)
    return a


def new_slide():
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.patch.set_facecolor(BG)
    fig.patches.append(plt.Rectangle((0, 0.992), 0.5, 0.008,
                       transform=fig.transFigure, facecolor=UKBLUE, zorder=6))
    fig.patches.append(plt.Rectangle((0.5, 0.992), 0.5, 0.008,
                       transform=fig.transFigure, facecolor=CNRED, zorder=6))
    return fig


def slide_chrome(fig, num, kick, title, sub):
    fig.text(0.08, 0.93, num, fontsize=12, color=GOLD, fontweight="bold",
             family="Consolas")
    fig.text(0.14, 0.93, kick.upper(), fontsize=12, color=MUTED,
             fontweight="bold", family="Consolas")
    fig.text(0.08, 0.875, title, fontsize=23, fontweight="bold", va="top",
             linespacing=1.1)
    fig.text(0.08, 0.80, sub, fontsize=11, color=MUTED, va="top",
             linespacing=1.4)
    fig.text(0.08, 0.035, "Ibtisam Ahmed Khan  ·  MSc, Tsinghua University",
             fontsize=8.5, color=MUTED)
    fig.text(0.92, 0.035, "QS 2026 · THE rankings", fontsize=8.5,
             color=MUTED, ha="right")


def style(ax):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.grid(axis="y", color=EDGE, lw=0.5)


# ------------------------------------------------------------- slides
def slide_title(p=1.0):
    fig = new_slide()
    fig.text(0.08, 0.70, "UK", fontsize=58, fontweight="bold", color=UKBLUE)
    fig.text(0.32, 0.715, "vs", fontsize=30, color=MUTED, style="italic")
    fig.text(0.08, 0.60, "CHINA", fontsize=58, fontweight="bold", color=CNRED)
    fig.text(0.08, 0.52, "Top 5 universities, head to head", fontsize=16,
             color=TEXT)
    fig.text(0.08, 0.475, "Oxford  ·  Cambridge  ·  Imperial  ·  UCL  ·  LSE",
             fontsize=10.5, color=UKBLUE)
    fig.text(0.08, 0.448, "Tsinghua  ·  Peking  ·  Fudan  ·  SJTU  ·  Zhejiang",
             fontsize=10.5, color=CNRED)
    fig.text(0.08, 0.31, f"-{int(tsinghua_rise * p)}", fontsize=66,
             color=GOLD, fontweight="bold")
    fig.text(0.08, 0.25, "places Tsinghua climbed in the world rankings\n"
             "since 2016 (THE: #47 to #12)", fontsize=12, color=MUTED,
             linespacing=1.5)
    fig.text(0.08, 0.06, "A data story by Ibtisam Ahmed Khan", fontsize=10,
             color=MUTED)
    return fig


def slide_rise(p=1.0):
    fig = new_slide()
    slide_chrome(fig, "01", "the rise", "Chinese universities are\nstorming up the table",
                 "Times Higher Education world rank, 2016-2025. Lower is better.")
    ax = fig.add_axes([0.13, 0.13, 0.74, 0.52])
    style(ax)
    series = [("Oxford", UKBLUE), ("Cambridge", "#86B4FF"),
              ("Imperial College London", "#3D7DE0"),
              ("Tsinghua", CNRED), ("Peking", "#FF8A8A")]
    k = max(int(len(YEARS) * p), 2)
    for name, col in series:
        ax.plot(YEARS[:k], hist[name].values[:k], color=col, lw=2.6)
    if p >= 1:
        placed, gap = [], 2.6
        for name, col in sorted(series, key=lambda nc: hist[nc[0]].iloc[-1]):
            yv = hist[name].iloc[-1]
            yv = yv if not placed else max(yv, placed[-1] + gap)
            placed.append(yv)
            ax.annotate(f"{SHORT(name)} #{hist[name].iloc[-1]:.0f}",
                        (YEARS[-1], yv), fontsize=10, color=col,
                        fontweight="bold", textcoords="offset points",
                        xytext=(8, 0), va="center")
    ax.set_xlim(2016, 2028.5)
    ax.set_ylim(52, 0)
    ax.set_yticks([1, 10, 20, 30, 40, 50])
    ax.tick_params(labelsize=10)
    return fig


def slide_versus(p=1.0):
    fig = new_slide()
    slide_chrome(fig, "02", "head to head",
                 "Two very different models",
                 "Average across each country's top 5 universities.")
    fig.text(0.28, 0.69, "UK", fontsize=15, color=UKBLUE, ha="center",
             fontweight="bold")
    fig.text(0.66, 0.69, "CHINA", fontsize=15, color=CNRED, ha="center",
             fontweight="bold")
    y0 = 0.61
    for label, ukv, cnv, fmt, mode in VERSUS:
        if mode == "year":
            base, mx = 1050, 1920
            ukf, cnf = (ukv - base) / (mx - base), (cnv - base) / (mx - base)
        else:
            mx = max(ukv, cnv)
            ukf, cnf = ukv / mx, cnv / mx
        fig.text(0.47, y0 + 0.045, label, fontsize=12, color=TEXT,
                 ha="center", fontweight="bold")
        for frac, col, sign in ((ukf, UKBLUE, -1), (cnf, CNRED, 1)):
            w = 0.165 * frac * p
            fig.patches.append(plt.Rectangle(
                (0.47 + 0.02 * sign, y0 - 0.006), w * sign, 0.022,
                transform=fig.transFigure, facecolor=col, zorder=4))
        if p > 0.5:
            fig.text(0.245, y0 - 0.003, fmt(ukv), fontsize=12, color=TEXT,
                     ha="right", family="Consolas")
            fig.text(0.695, y0 - 0.003, fmt(cnv), fontsize=12, color=TEXT,
                     ha="left", family="Consolas")
        y0 -= 0.13
    fig.text(0.08, 0.115, "Founded-year bars scaled 1050-1920. UK elites are "
             "centuries older;\nChinese giants are larger and far less "
             "international.", fontsize=9.5, color=MUTED, linespacing=1.5)
    return fig


def slide_bars(p, col_metric, title, sub, num, kick, fmt):
    fig = new_slide()
    slide_chrome(fig, num, kick, title, sub)
    ax = fig.add_axes([0.27, 0.12, 0.62, 0.55])
    ax.set_facecolor(BG)
    order = uni.sort_values(col_metric)
    vals = order[col_metric].values * p
    cols = [UKBLUE if c == "UK" else CNRED for c in order.country]
    ax.barh(range(len(order)), vals, color=cols, height=0.72)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([SHORT(n) for n in order.university], fontsize=10)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([])
    mx = order[col_metric].max()
    for i, v in enumerate(vals):
        if v > 0:
            ax.text(v + mx * 0.015, i, fmt(v), va="center", fontsize=9.5,
                    color=MUTED)
    ax.set_xlim(0, mx * 1.16)
    return fig


def slide_close(p=1.0):
    fig = new_slide()
    fig.text(0.08, 0.88, "THE TAKEAWAYS", fontsize=15, color=GOLD,
             fontweight="bold", family="Consolas")
    items = [
        ("Oxford #1", "has topped Times Higher Education every\nyear since 2017"),
        (f"+{int(tsinghua_rise)} / +{int(peking_rise)}", "places climbed by Tsinghua and Peking\n"
         "in the world rankings since 2016"),
        ("54% vs 12%", "international students: the UK's top 5\nare far more global than China's"),
        ("62k vs 13k", "biggest to smallest student body:\nZhejiang dwarfs LSE"),
    ]
    y = 0.74
    for big, small in items:
        fig.text(0.08, y, big, fontsize=30, color=TEXT, fontweight="bold")
        fig.text(0.08, y - 0.052, small, fontsize=11.5, color=MUTED,
                 linespacing=1.45)
        y -= 0.155
    fig.text(0.08, 0.10, "Full code and data on GitHub", fontsize=12,
             color=GOLD)
    fig.text(0.08, 0.06, "Ibtisam Ahmed Khan  ·  MSc, Tsinghua University",
             fontsize=10, color=MUTED)
    return fig


# ------------------------------------------------------------- assemble GIF
frames = []


def reveal(slide_fn, steps, lo=0.12):
    for t in np.linspace(lo, 1, steps):
        frames.append(fig_to_frame(slide_fn(ease(t))))


def hold(slide_fn, n):
    f = fig_to_frame(slide_fn(1.0))
    frames.extend([f] * n)


reveal(slide_title, 6); hold(slide_title, 6)
reveal(slide_rise, 8); hold(slide_rise, 7)
reveal(slide_versus, 6); hold(slide_versus, 7)
reveal(lambda p=1.0: slide_bars(p, "intl_pct", "How global are they?",
       "International student share (%). The UK's clear edge.", "03",
       "how global", lambda v: f"{v:.0f}%"), 5)
hold(lambda p=1.0: slide_bars(p, "intl_pct", "How global are they?",
     "International student share (%). The UK's clear edge.", "03",
     "how global", lambda v: f"{v:.0f}%"), 7)
reveal(lambda p=1.0: slide_bars(p, "students_thousands", "Size of the campus",
       "Students (thousands). Chinese campuses are far larger.", "04",
       "student body", lambda v: f"{v:.0f}k"), 5)
hold(lambda p=1.0: slide_bars(p, "students_thousands", "Size of the campus",
     "Students (thousands). Chinese campuses are far larger.", "04",
     "student body", lambda v: f"{v:.0f}k"), 7)
hold(slide_close, 12)

imageio.mimsave("gifs/uk_vs_china_universities_poster.gif", frames, fps=3, loop=0)
print("GIF frames:", len(frames))
try:
    imageio.mimsave("gifs/uk_vs_china_universities_poster.mp4", frames, fps=3)
    print("MP4 written")
except Exception as e:
    print("MP4 skipped:", e)

# ------------------------------------------------------------- static overview
fig = new_slide()
fig.text(0.06, 0.95, "UK", fontsize=22, fontweight="bold", color=UKBLUE)
fig.text(0.12, 0.95, "vs", fontsize=15, color=MUTED, style="italic")
fig.text(0.17, 0.95, "CHINA", fontsize=22, fontweight="bold", color=CNRED)
fig.text(0.06, 0.928, "Top 5 universities, head to head", fontsize=10,
         color=MUTED)
# rise mini
ax = fig.add_axes([0.10, 0.66, 0.83, 0.20]); style(ax)
for name, col in [("Oxford", UKBLUE), ("Cambridge", "#86B4FF"),
                  ("Imperial College London", "#3D7DE0"), ("Tsinghua", CNRED),
                  ("Peking", "#FF8A8A")]:
    ax.plot(YEARS, hist[name].values, color=col, lw=1.8)
    ax.annotate(f"{SHORT(name)} #{hist[name].iloc[-1]:.0f}",
                (YEARS[-1], hist[name].iloc[-1]), fontsize=6.5, color=col,
                fontweight="bold", textcoords="offset points", xytext=(4, 0))
ax.set_xlim(2016, 2029); ax.set_ylim(52, 0); ax.set_yticks([1, 20, 40])
ax.tick_params(labelsize=7)
fig.text(0.06, 0.875, "THE world rank, 2016-2025 (lower is better)",
         fontsize=8, color=GOLD, fontweight="bold")
# intl + size minis
for axpos, metric, ttl, fm in [
        ([0.30, 0.36, 0.62, 0.22], "intl_pct", "International students (%)",
         lambda v: f"{v:.0f}%"),
        ([0.30, 0.07, 0.62, 0.22], "students_thousands", "Students (000s)",
         lambda v: f"{v:.0f}k")]:
    ax = fig.add_axes(axpos); ax.set_facecolor(BG)
    order = uni.sort_values(metric)
    ax.barh(range(len(order)), order[metric].values,
            color=[UKBLUE if c == "UK" else CNRED for c in order.country],
            height=0.7)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([SHORT(n) for n in order.university], fontsize=7)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([])
    for i, v in enumerate(order[metric].values):
        ax.text(v + order[metric].max() * 0.015, i, fm(v), va="center",
                fontsize=6.5, color=MUTED)
    ax.set_xlim(0, order[metric].max() * 1.16)
    fig.text(0.06, axpos[1] + axpos[3] + 0.005, ttl, fontsize=8, color=GOLD,
             fontweight="bold")
fig.text(0.06, 0.025, "Ibtisam Ahmed Khan  ·  QS 2026 & THE rankings  ·  "
         "for illustration", fontsize=7, color=MUTED)
fig.savefig("charts/poster_static.png", dpi=150, facecolor=BG)
plt.close(fig)

print("\nTsinghua THE 2016->2025:", hist["Tsinghua"].iloc[0], "->",
      hist["Tsinghua"].iloc[-1])
for label, ukv, cnv, fmt, mode in VERSUS:
    print(f"{label:28s} UK {fmt(ukv):>8s}   CN {fmt(cnv):>8s}")
