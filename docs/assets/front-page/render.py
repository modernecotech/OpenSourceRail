"""Render the README's charts and animations from published example data."""

import gzip
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent
ROOT = ASSETS.parents[2]
BACKGROUND = "#f8fafc"
INK = "#172b3b"
MUTED = "#42566b"
TEAL = "#006b69"
BLUE = "#2d63a0"
ORANGE = "#ac4f21"
FONT_PATH = Path(matplotlib.get_data_path()) / "fonts/ttf"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.facecolor": BACKGROUND, "figure.facecolor": BACKGROUND,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#b7c6d2", "savefig.facecolor": BACKGROUND,
})


def figure(title, subtitle, footer):
    fig, ax = plt.subplots(figsize=(8.4, 4.4), dpi=115)
    fig.subplots_adjust(left=.12, right=.94, bottom=.22, top=.75)
    fig.text(.045, .92, title, fontsize=18, weight="bold")
    fig.text(.045, .84, subtitle, color=MUTED)
    fig.text(.045, .048, footer, fontsize=9, color=MUTED)
    ax.grid(axis="y", color="#d5dfe7", linewidth=.65)
    ax.set_axisbelow(True)
    return fig, ax


def save_chart(fig, name):
    fig.savefig(ASSETS / name)
    plt.close(fig)


def read_data_js(path):
    source = (ROOT / path).read_text()
    return json.loads(source.split("=", 1)[1].strip().removesuffix(";"))


def span_chart():
    text = (ROOT / "cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md").read_text()
    pattern = r"\| (\d+)m U [\d.]+m / shared \| ([\d,]+) \| ([\d.]+) t at 12 m \| \$([\d,.]+)m \|"
    rows = re.findall(pattern, text)
    spans, placements, tonnes, costs = zip(*rows, strict=True)
    x = list(map(int, spans))
    fig, ax = figure(
        "Longer girders change the erection job",
        "Shared-pier U-girders · identical double-track scope in the Baghdad Airport audit",
        "Loads are at 12 m working radius. Closure bays and site works need separate pricing.",
    )
    ax.bar(x, list(map(float, costs)), width=2.8, color=[BLUE, BLUE, TEAL])
    ax.set(xticks=x, xticklabels=[f"{s} m span" for s in spans], ylim=(0, 246),
           ylabel="30-year present value (US$ million)")
    for span, count, hook, cost in rows:
        ax.annotate(f"${cost}m\n{count} placements\n{hook} t at hook",
                    (int(span), float(cost)), xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color=INK)
    save_chart(fig, "span-erection.png")


def finance_chart():
    data = read_data_js("docs/operator-review/finance/schedules.js")["core"]["cases"]["mixed_debt"]
    rows = data["annual"]
    years = [r["year"] for r in rows]
    amounts = [
        ("Capital less borrowing", BLUE, [r["capital"] - r["borrowing"] for r in rows]),
        ("Principal and interest", "#644594", [r["principal"] + r["interest"] for r in rows]),
        ("Operations", TEAL, [r["operations"] for r in rows]),
        ("Renewals", ORANGE, [r["renewals"] for r in rows]),
    ]
    fig, ax = figure(
        "What the railway buyer pays each year",
        "Core digital example · 50% borrowed · 4% real interest · 20-year repayment",
        "Illustrative owner cash before fare receipts, in constant 2026 US dollars. Year 5 is first full service.",
    )
    baseline = [0.0] * len(rows)
    for label, colour, values in amounts:
        ax.bar(years, values, bottom=baseline, label=label, color=colour, width=.82)
        baseline = [low + value for low, value in zip(baseline, values, strict=True)]
    if any(abs(sum_ - r["buyer_cash"]) > 1e-6 for sum_, r in zip(baseline, rows, strict=True)):
        raise ValueError("Annual cash components do not match source totals")
    ax.set(xticks=[1, 5, 10, 15, 19, 24, 29, 34], xlabel="Programme year",
           ylabel="Buyer cash (US$ million)", xlim=(0, 35))
    ax.legend(loc="upper left", ncol=2, fontsize=8.5, frameon=False)
    save_chart(fig, "annual-funding.png")


def trip_chart_and_animation():
    with gzip.open(ROOT / "docs/design-engine/station-pair/study.json.gz", "rt") as stream:
        cases = json.load(stream)["cases"]
    case, = (c for c in cases if c["summary"]["name"] == "Powered wheels / 8 driven axles"
             and c["summary"]["distance_m"] == 1500 and c["summary"]["speed_cap_km_h"] == 50)
    trace = case["journey"]["trace"]
    times = [row["time_s"] for row in trace]
    speeds = [row["speed_m_s"] * 3.6 for row in trace]
    fig, ax = figure(
        "Follow the train between two stations",
        "1.5 km research case · 8 driven axles · 50 km/h speed cap",
        "Published numerical trace with feedback braking. The operating map and physical acceptance remain open.",
    )
    ax.plot(times, speeds, color=TEAL, lw=2.5)
    ax.fill_between(times, speeds, 0, color=TEAL, alpha=.12)
    ax.set(xlim=(0, 200), ylim=(0, 57), xlabel="Elapsed simulated time (s)",
           ylabel="Train speed (km/h)")
    ax.axhline(50, ls="--", lw=1, color=BLUE)
    ax.annotate("Speed cap", (4, 50), xytext=(0, 4), textcoords="offset points", color=BLUE)
    save_chart(fig, "station-pair-speed.png")

    frames = []
    for index in range(46):
        row = trace[round(index / 45 * (len(trace) - 1))]
        frame, draw = canvas(
            "One simulated trip in 9 seconds",
            "Station-pair research · 1.5 km · 8 driven axles",
        )
        left, right = 73, 727
        x = left + (right - left) * row["position_m"] / 1500
        draw.line((left, 152, right, 152), fill="#9cb1c2", width=7)
        draw.line((left, 152, x, 152), fill=TEAL, width=7)
        for stop in (left, right):
            draw.ellipse((stop-8, 144, stop+8, 160), fill=INK)
        draw.rounded_rectangle((x-20, 123, x+20, 145), radius=6, fill=TEAL)
        label(draw, (41, 174), "Departure", 17)
        label(draw, (678, 174), "Berth target", 17)
        label(draw, (42, 224), f"{row['time_s']:.0f} s elapsed       "
              f"{row['position_m']:,.1f} m travelled       {row['speed_m_s'] * 3.6:.1f} km/h", 23, bold=True)
        label(draw, (42, 267), "Position and speed from the published numerical trace.", 16, colour=MUTED)
        frames.append(frame)
    write_gif(frames, "station-pair-motion.gif", [190] * 45 + [1200])


def label(draw, position, text, size, *, bold=False, colour=INK):
    font = ImageFont.truetype(str(FONT_PATH / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)
    draw.text(position, text, font=font, fill=colour)


def canvas(title, subtitle):
    frame = Image.new("RGB", (800, 306), BACKGROUND)
    draw = ImageDraw.Draw(frame)
    label(draw, (36, 22), title, 29, bold=True)
    label(draw, (36, 68), subtitle, 17, colour=MUTED)
    return frame, draw


def write_gif(frames, name, duration):
    frames[0].save(ASSETS / name, append_images=frames[1:], save_all=True,
                   duration=duration, disposal=1, optimize=True)


def alarm_animation():
    replay = read_data_js("docs/operator-review/screens/replay-data.js")
    images = []
    for frame in replay["frames"]:
        row, = (row for row in frame["rows"] if row["asset"] == "section-01")
        colour = ORANGE if row["active"] else TEAL
        image, draw = canvas("Can the control room clear the alarm?",
                             "Gateway replay · simulated section protection readings")
        draw.rounded_rectangle((36, 111, 764, 243), radius=12, fill="#e6edf3")
        label(draw, (56, 129), frame["name"], 24, bold=True)
        label(draw, (56, 170), f"Replay time {frame['time']}  ·  Last sample {row['source_time']}", 18)
        label(draw, (56, 204), f"Reading {row['quality']}  /  "
              f"Trip {'active' if row['active'] else 'clear'}", 20, bold=True, colour=colour)
        label(draw, (36, 263), "The stale sample leaves the trip active until a fresh clear arrives.", 16, colour=MUTED)
        images.append(image)
    write_gif(images, "section-alarm-replay.gif", [1550, 1750, 2250, 2250])


if __name__ == "__main__":
    span_chart()
    finance_chart()
    trip_chart_and_animation()
    alarm_animation()
