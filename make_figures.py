from pathlib import Path
from html import escape

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "processed" / "resource_panel_with_controls.csv"
CONTROL_RESULTS = ROOT / "data" / "processed" / "results" / "growth_control_regression_coefficients.csv"
BASE_RESULTS = ROOT / "data" / "processed" / "results" / "resource_curse_regression_coefficients.csv"
FIGURE_DIR = ROOT / "data" / "processed" / "results" / "figures"


def svg_header(width, height, title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#182230}.title{font-size:25px;font-weight:700}.subtitle{font-size:14px;fill:#536273}.axis{font-size:13px}.small{font-size:12px;fill:#536273}.label{font-size:14px;font-weight:600}</style>',
        f'<text x="70" y="42" class="title">{escape(title)}</text>',
        f'<text x="70" y="68" class="subtitle">{escape(subtitle)}</text>',
    ]


def save_binned_chart():
    data = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    data["total_resource_rents_pct_gdp"] = pd.to_numeric(
        data["total_resource_rents_pct_gdp"], errors="coerce"
    )
    data["gdp_per_capita_growth_pct"] = pd.to_numeric(
        data["gdp_per_capita_growth_pct"], errors="coerce"
    )
    data = data.dropna(subset=["total_resource_rents_pct_gdp", "gdp_per_capita_growth_pct"])
    bins = [-float("inf"), 1, 5, 15, float("inf")]
    labels = ["≤ 1%", ">1–5%", ">5–15%", ">15%"]
    data["rent_group"] = pd.cut(
        data["total_resource_rents_pct_gdp"], bins=bins, labels=labels, right=True
    )
    stats = data.groupby("rent_group", observed=False)["gdp_per_capita_growth_pct"].agg(
        n="count", q1=lambda x: x.quantile(.25), median="median", q3=lambda x: x.quantile(.75)
    ).dropna()

    width, height = 1000, 620
    left, right, top, bottom = 150, 940, 120, 500
    y_min = min(-10, float(stats["q1"].min()))
    y_max = max(15, float(stats["q3"].max()))
    pad = (y_max - y_min) * .08
    y_min -= pad
    y_max += pad
    y = lambda value: bottom - (value - y_min) / (y_max - y_min) * (bottom - top)
    x_positions = [left + (i + .5) * (right - left) / len(labels) for i in range(len(labels))]

    lines = svg_header(
        width, height,
        "Resource rents and GDP per capita growth",
        "Descriptive country-year medians by rent-to-GDP range; bars show the interquartile range (2000–2021)",
    )
    for tick in range(int(y_min // 5 * 5), int(y_max // 5 * 5) + 6, 5):
        if tick < y_min or tick > y_max:
            continue
        yy = y(tick)
        lines.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#e5eaf0"/>')
        lines.append(f'<text x="{left-14}" y="{yy+4:.1f}" text-anchor="end" class="axis">{tick}%</text>')

    for i, label in enumerate(labels):
        if label not in stats.index:
            continue
        row = stats.loc[label]
        xx = x_positions[i]
        y1, ym, y3 = y(row["q1"]), y(row["median"]), y(row["q3"])
        lines.extend([
            f'<line x1="{xx:.1f}" y1="{y3:.1f}" x2="{xx:.1f}" y2="{y1:.1f}" stroke="#1877a8" stroke-width="8" stroke-linecap="round"/>',
            f'<line x1="{xx-14:.1f}" y1="{y3:.1f}" x2="{xx+14:.1f}" y2="{y3:.1f}" stroke="#125b82" stroke-width="2"/>',
            f'<line x1="{xx-14:.1f}" y1="{y1:.1f}" x2="{xx+14:.1f}" y2="{y1:.1f}" stroke="#125b82" stroke-width="2"/>',
            f'<circle cx="{xx:.1f}" cy="{ym:.1f}" r="8" fill="#f08a24" stroke="white" stroke-width="2"/>',
            f'<text x="{xx:.1f}" y="{bottom+28}" text-anchor="middle" class="label">{escape(label)}</text>',
            f'<text x="{xx:.1f}" y="{bottom+50}" text-anchor="middle" class="small">n={int(row["n"]):,}</text>',
        ])
    lines.extend([
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#526170"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#526170"/>',
        f'<text x="{(left+right)/2}" y="{height-25}" text-anchor="middle" class="axis">Total natural resource rents (% of GDP)</text>',
        f'<text x="35" y="{(top+bottom)/2}" transform="rotate(-90 35 {(top+bottom)/2})" text-anchor="middle" class="axis">GDP per capita growth (%)</text>',
        f'<circle cx="170" cy="570" r="7" fill="#f08a24"/><text x="184" y="575" class="small">Median</text>',
        '<line x1="270" y1="570" x2="300" y2="570" stroke="#1877a8" stroke-width="7"/><text x="310" y="575" class="small">25th–75th percentile</text>',
        '<text x="580" y="575" class="small">Pooled observations; not adjusted for country or year effects.</text>',
        '</svg>',
    ])
    (FIGURE_DIR / "resource_rents_by_growth_bins.svg").write_text("\n".join(lines), encoding="utf-8")


def save_coefficient_chart():
    controls = pd.read_csv(CONTROL_RESULTS, encoding="utf-8-sig")
    baseline = pd.read_csv(BASE_RESULTS, encoding="utf-8-sig")
    rent = "total_resource_rents_pct_gdp"
    rows = []
    # Keep baseline as historical reference; other estimates come from matched control specs.
    first = baseline[
        (baseline["outcome_variable"] == "gdp_per_capita_growth_pct")
        & (baseline["predictor"] == rent)
    ].iloc[0]
    rows.append({
        "label": "Baseline, 2000–2021",
        "coefficient": first["coefficient"], "lo": first["ci_95_low"],
        "hi": first["ci_95_high"], "n": first["observations"],
    })
    labels = {
        "Core controls: lagged log GDP per capita + population growth": "Core controls, current-year rents",
        "Expanded controls: core + investment + trade": "Core + investment + trade",
        "Previous-year rents on lag-comparison sample": "Core controls, previous-year rents",
    }
    for model, label in labels.items():
        variable = "resource_rents_pct_gdp_previous_year" if "Previous-year" in model else rent
        row = controls[(controls["model"] == model) & (controls["variable"] == variable)].iloc[0]
        rows.append({"label": label, "coefficient": row["coefficient"], "lo": row["ci_95_low"], "hi": row["ci_95_high"], "n": row["observations"]})

    frame = pd.DataFrame(rows)
    width, height = 1080, 430
    left, right, top, bottom = 410, 1005, 110, 340
    x_min = min(-.12, float(frame["lo"].min()) - .02)
    x_max = max(.34, float(frame["hi"].max()) + .02)
    x = lambda value: left + (value - x_min) / (x_max - x_min) * (right - left)
    y_positions = [top + 28 + i * 67 for i in range(len(frame))]
    lines = svg_header(
        width, height,
        "Estimated association between resource rents and GDP per capita growth",
        "Two-way fixed effects; bars show 95% confidence intervals; standard errors clustered by country",
    )
    for tick in [i / 100 for i in range(int(x_min * 100 // 5 * 5), int(x_max * 100 // 5 * 5) + 6, 5)]:
        if tick < x_min or tick > x_max:
            continue
        xx = x(tick)
        lines.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{bottom}" stroke="{"#aab5c2" if abs(tick)<1e-9 else "#e7ebef"}" stroke-dasharray="{"4 4" if abs(tick)<1e-9 else "none"}"/>')
        lines.append(f'<text x="{xx:.1f}" y="{bottom+23}" text-anchor="middle" class="axis">{tick:.2f}</text>')
    for i, row in frame.iterrows():
        yy = y_positions[i]
        color = "#bd5b37" if "previous-year" in row["label"] else "#147a62"
        lines.extend([
            f'<text x="{left-18}" y="{yy+5}" text-anchor="end" class="label">{escape(row["label"])}</text>',
            f'<text x="{left-18}" y="{yy+23}" text-anchor="end" class="small">n={int(row["n"]):,}</text>',
            f'<line x1="{x(row["lo"]):.1f}" y1="{yy}" x2="{x(row["hi"]):.1f}" y2="{yy}" stroke="{color}" stroke-width="4"/>',
            f'<line x1="{x(row["lo"]):.1f}" y1="{yy-7}" x2="{x(row["lo"]):.1f}" y2="{yy+7}" stroke="{color}" stroke-width="2"/>',
            f'<line x1="{x(row["hi"]):.1f}" y1="{yy-7}" x2="{x(row["hi"]):.1f}" y2="{yy+7}" stroke="{color}" stroke-width="2"/>',
            f'<circle cx="{x(row["coefficient"]):.1f}" cy="{yy}" r="7" fill="{color}"/>',
        ])
    lines.extend([
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#526170"/>',
        f'<text x="{(left+right)/2}" y="{height-32}" text-anchor="middle" class="axis">Coefficient: percentage-point change in GDP per capita growth per 1 pp of rents/GDP</text>',
        '<text x="70" y="395" class="small">Different samples/specifications are shown. Read the estimate and its interval, not just statistical significance.</text>',
        '</svg>',
    ])
    (FIGURE_DIR / "growth_regression_coefficients.svg").write_text("\n".join(lines), encoding="utf-8")


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    for path in [DATA_FILE, CONTROL_RESULTS, BASE_RESULTS]:
        if not path.exists():
            raise SystemExit(f"ไม่พบไฟล์ที่ต้องใช้: {path}")
    save_binned_chart()
    save_coefficient_chart()
    print(f"สร้างกราฟ SVG ใน {FIGURE_DIR}")


if __name__ == "__main__":
    main()
