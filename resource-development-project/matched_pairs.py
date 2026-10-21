"""Matched-pairs comparison of GDP per capita growth in low/high rent years.

Each country/economy is its own pair. Within each unit, years are classified
using the 33rd and 67th percentiles of observed resource rents. The middle
third is omitted. The paired outcome is mean GDP per capita growth in high-
rent years minus the mean in low-rent years.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parent
INPUT_CANDIDATES = [
    ROOT / "data" / "processed" / "resource_panel_with_controls.csv",
    ROOT / "data" / "processed" / "resource_panel_all.csv",
]
OUTPUT_DIR = ROOT / "data" / "processed" / "results"
LOW_QUANTILE = 1 / 3
HIGH_QUANTILE = 2 / 3
MIN_YEARS_PER_GROUP = 3
CONFIDENCE_LEVEL = 0.95

COUNTRY = "Country Code"
COUNTRY_NAME = "Country Name"
YEAR = "Year"
RENTS = "total_resource_rents_pct_gdp"
OUTCOME = "gdp_per_capita_growth_pct"


def choose_input() -> Path:
    for candidate in INPUT_CANDIDATES:
        if candidate.exists():
            return candidate
    candidates = "\n".join(str(path) for path in INPUT_CANDIDATES)
    raise FileNotFoundError(f"ไม่พบไฟล์ข้อมูลที่ต้องใช้:\n{candidates}")


def main() -> None:
    input_path = choose_input()
    data = pd.read_csv(input_path)
    required = {COUNTRY, COUNTRY_NAME, YEAR, RENTS, OUTCOME}
    missing_columns = required.difference(data.columns)
    if missing_columns:
        raise ValueError(f"ไม่พบคอลัมน์ที่ต้องใช้: {sorted(missing_columns)}")

    data[YEAR] = pd.to_numeric(data[YEAR], errors="coerce")
    data[RENTS] = pd.to_numeric(data[RENTS], errors="coerce")
    data[OUTCOME] = pd.to_numeric(data[OUTCOME], errors="coerce")
    data = data.dropna(subset=[COUNTRY, YEAR]).copy()
    data[YEAR] = data[YEAR].astype(int)
    if data.duplicated([COUNTRY, YEAR]).any():
        duplicates = data.loc[data.duplicated([COUNTRY, YEAR], keep=False), [COUNTRY, YEAR]]
        raise ValueError(
            "พบ Country Code-Year ซ้ำ จึงหยุดเพื่อป้องกันการนับข้อมูลซ้ำ:\n"
            + duplicates.head(10).to_string(index=False)
        )

    valid = data.loc[
        np.isfinite(data[RENTS]) & np.isfinite(data[OUTCOME]),
        [COUNTRY, COUNTRY_NAME, YEAR, RENTS, OUTCOME],
    ].copy()
    country_results = []
    country_year_groups = []
    exclusions = {
        "fewer_than_2x_min_years": 0,
        "indistinguishable_rent_cutoffs": 0,
        "too_few_years_in_a_group": 0,
    }

    for country_code, group in valid.groupby(COUNTRY, dropna=False, sort=True):
        group = group.sort_values(YEAR).copy()
        names = group[COUNTRY_NAME].dropna().astype(str).mode()
        country_name = names.iloc[0] if len(names) else str(country_code)
        if len(group) < 2 * MIN_YEARS_PER_GROUP:
            exclusions["fewer_than_2x_min_years"] += 1
            continue

        low_cutoff = float(group[RENTS].quantile(LOW_QUANTILE, interpolation="linear"))
        high_cutoff = float(group[RENTS].quantile(HIGH_QUANTILE, interpolation="linear"))
        if not low_cutoff < high_cutoff:
            exclusions["indistinguishable_rent_cutoffs"] += 1
            continue

        group["rent_exposure_group"] = np.select(
            [group[RENTS] <= low_cutoff, group[RENTS] >= high_cutoff],
            ["low", "high"],
            default="middle_excluded",
        )
        low = group.loc[group["rent_exposure_group"].eq("low")]
        high = group.loc[group["rent_exposure_group"].eq("high")]
        if len(low) < MIN_YEARS_PER_GROUP or len(high) < MIN_YEARS_PER_GROUP:
            exclusions["too_few_years_in_a_group"] += 1
            continue

        low_mean = float(low[OUTCOME].mean())
        high_mean = float(high[OUTCOME].mean())
        country_results.append(
            {
                COUNTRY: country_code,
                COUNTRY_NAME: country_name,
                "low_rent_cutoff_pct_gdp": low_cutoff,
                "high_rent_cutoff_pct_gdp": high_cutoff,
                "low_rent_years": len(low),
                "high_rent_years": len(high),
                "low_rent_mean_gdp_per_capita_growth_pct": low_mean,
                "high_rent_mean_gdp_per_capita_growth_pct": high_mean,
                "paired_difference_high_minus_low_pp": high_mean - low_mean,
                "valid_years_used": len(group),
                "first_year": int(group[YEAR].min()),
                "last_year": int(group[YEAR].max()),
            }
        )
        country_year_groups.append(group)

    paired = pd.DataFrame(country_results)
    if len(paired) < 2:
        raise ValueError(
            f"มีคู่ประเทศไม่พอสำหรับ paired t-test (พบ {len(paired)} คู่). "
            "ตรวจข้อมูลและเกณฑ์การจัดกลุ่มก่อนวิเคราะห์"
        )

    differences = paired["paired_difference_high_minus_low_pp"].to_numpy(dtype=float)
    n_pairs = len(differences)
    mean_difference = float(np.mean(differences))
    sd_difference = float(np.std(differences, ddof=1))
    cohens_dz = mean_difference / sd_difference if sd_difference else np.nan
    standard_error = sd_difference / np.sqrt(n_pairs)
    critical_value = float(stats.t.ppf((1 + CONFIDENCE_LEVEL) / 2, df=n_pairs - 1))
    ci_low = mean_difference - critical_value * standard_error
    ci_high = mean_difference + critical_value * standard_error
    paired_t = stats.ttest_1samp(differences, popmean=0.0, alternative="two-sided")

    nonzero_differences = differences[~np.isclose(differences, 0.0)]
    if len(nonzero_differences):
        wilcoxon = stats.wilcoxon(
            differences,
            alternative="two-sided",
            zero_method="wilcox",
            method="auto",
        )
        wilcoxon_statistic = float(wilcoxon.statistic)
        wilcoxon_p = float(wilcoxon.pvalue)
    else:
        wilcoxon_statistic = 0.0
        wilcoxon_p = 1.0

    summary = pd.DataFrame(
        [
            {
                "input_file": str(input_path.relative_to(ROOT)),
                "years_in_panel_start": int(valid[YEAR].min()),
                "years_in_panel_end": int(valid[YEAR].max()),
                "units_in_panel": int(data[COUNTRY].nunique()),
                "units_without_any_complete_rent_outcome_year": int(data[COUNTRY].nunique() - valid[COUNTRY].nunique()),
                "country_pairs": n_pairs,
                "low_rent_years_per_country_minimum": MIN_YEARS_PER_GROUP,
                "low_rent_percentile_cutoff": LOW_QUANTILE,
                "high_rent_percentile_cutoff": HIGH_QUANTILE,
                "mean_low_rent_growth_pct": float(paired["low_rent_mean_gdp_per_capita_growth_pct"].mean()),
                "mean_high_rent_growth_pct": float(paired["high_rent_mean_gdp_per_capita_growth_pct"].mean()),
                "mean_difference_high_minus_low_pp": mean_difference,
                "median_paired_difference_pp": float(np.median(differences)),
                "sd_paired_difference_pp": sd_difference,
                "standard_error_pp": standard_error,
                "ci_95_low_pp": ci_low,
                "ci_95_high_pp": ci_high,
                "paired_t_statistic": float(paired_t.statistic),
                "paired_t_p_value_two_sided": float(paired_t.pvalue),
                "cohens_dz_paired": cohens_dz,
                "wilcoxon_statistic_sensitivity": wilcoxon_statistic,
                "wilcoxon_p_value_two_sided_sensitivity": wilcoxon_p,
                "countries_high_gt_low": int((differences > 0).sum()),
                "countries_low_gt_high": int((differences < 0).sum()),
                "countries_tied": int(np.isclose(differences, 0.0).sum()),
                "excluded_fewer_than_minimum_total_years": exclusions["fewer_than_2x_min_years"],
                "excluded_indistinguishable_cutoffs": exclusions["indistinguishable_rent_cutoffs"],
                "excluded_too_few_years_in_group": exclusions["too_few_years_in_a_group"],
                "valid_country_years_before_grouping": len(valid),
            }
        ]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / "matched_pairs_summary.csv"
    paired_path = OUTPUT_DIR / "matched_pairs_country_results.csv"
    groups_path = OUTPUT_DIR / "matched_pairs_country_year_groups.csv"
    report_path = OUTPUT_DIR / "matched_pairs_report.txt"
    figure_path = OUTPUT_DIR / "matched_pairs_growth_difference.svg"

    summary.to_csv(summary_path, index=False)
    paired.to_csv(paired_path, index=False)
    pd.concat(country_year_groups, ignore_index=True).to_csv(groups_path, index=False)

    p_value = float(paired_t.pvalue)
    decision = "reject H0" if p_value < 0.05 else "do not reject H0"
    report = f"""MATCHED-PAIRS ANALYSIS: GDP PER CAPITA GROWTH

Input: {input_path.relative_to(ROOT)}
Panel years: {valid[YEAR].min()}–{valid[YEAR].max()}
Units in source panel: {data[COUNTRY].nunique():,}
Valid country-years with both variables: {len(valid):,}
Units with no country-year having both variables: {data[COUNTRY].nunique() - valid[COUNTRY].nunique():,}
Country/economy pairs analyzed: {n_pairs:,}

Method
- Within each country/economy, years with observed rents and outcome were ranked by that unit's own resource rents (% GDP).
- Low-rent years are at or below the 33rd percentile; high-rent years are at or above the 67th percentile. The middle is omitted.
- At least {MIN_YEARS_PER_GROUP} valid years in each group were required. Units with identical low/high cutoffs were excluded.
- For each unit, difference = mean growth in high-rent years minus mean growth in low-rent years.
- Main test: two-sided paired t-test of whether the average country-level difference is zero; alpha = 0.05.
- Sensitivity check: two-sided Wilcoxon signed-rank test.
- Missing values were not imputed. Each country/economy receives equal weight in the paired test.

Results
Mean growth in low-rent years: {paired['low_rent_mean_gdp_per_capita_growth_pct'].mean():.4f}%
Mean growth in high-rent years: {paired['high_rent_mean_gdp_per_capita_growth_pct'].mean():.4f}%
Mean paired difference (high minus low): {mean_difference:.4f} percentage points
Median paired difference: {np.median(differences):.4f} percentage points
95% confidence interval: [{ci_low:.4f}, {ci_high:.4f}]
Paired t: t({n_pairs - 1}) = {float(paired_t.statistic):.4f}, p = {p_value:.6g}
Cohen's dz: {cohens_dz:.4f}
Wilcoxon signed-rank sensitivity: statistic = {wilcoxon_statistic:.4f}, p = {wilcoxon_p:.6g}
High-rent mean was greater in {int((differences > 0).sum())} pairs; lower in {int((differences < 0).sum())}; tied in {int(np.isclose(differences, 0.0).sum())}.
Decision at 5%: {decision}.

Exclusions
- No country-year with both variables: {data[COUNTRY].nunique() - valid[COUNTRY].nunique()}
- Too few valid years overall: {exclusions['fewer_than_2x_min_years']}
- Low/high rent cutoffs not distinct: {exclusions['indistinguishable_rent_cutoffs']}
- Fewer than {MIN_YEARS_PER_GROUP} years in either group: {exclusions['too_few_years_in_a_group']}

Interpretation and limits
This compares each country/economy's average growth in its own relatively high-rent years with its own relatively low-rent years. It does not estimate the change in growth for a one-percentage-point increase in rents. Pairing accounts for stable differences between countries, but this test does not control for common calendar-year shocks or other time-varying factors. It is an association, not evidence that resource rents cause growth to change. The Wilcoxon result is a sensitivity check and tests a rank-based paired difference, not the same mean-difference parameter as the t-test.
"""
    report_path.write_text(report, encoding="utf-8")

    ranked = paired["paired_difference_high_minus_low_pp"].sort_values().to_numpy()
    width, height = 1100, 650
    left, right, top, bottom = 100, 35, 100, 95
    plot_width, plot_height = width - left - right, height - top - bottom
    low_bound = min(float(ranked.min()), ci_low, 0.0)
    high_bound = max(float(ranked.max()), ci_high, 0.0)
    padding = max((high_bound - low_bound) * 0.06, 0.5)
    y_min, y_max = low_bound - padding, high_bound + padding

    def x_position(index: int) -> float:
        if n_pairs == 1:
            return left + plot_width / 2
        return left + (index / (n_pairs - 1)) * plot_width

    def y_position(value: float) -> float:
        return top + ((y_max - value) / (y_max - y_min)) * plot_height

    tick_count = 6
    ticks = np.linspace(y_min, y_max, tick_count)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Country-level paired differences in GDP per capita growth between high and low resource-rent years">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#202124}.grid{stroke:#d9d9d9;stroke-width:1}.axis{stroke:#333;stroke-width:1.4}</style>',
        '<text x="550" y="37" text-anchor="middle" font-size="25" font-weight="600">Within-country GDP per capita growth difference</text>',
        '<text x="550" y="66" text-anchor="middle" font-size="17">High-rent years minus low-rent years</text>',
        f'<text x="{left}" y="88" font-size="14">Paired t-test: N = {n_pairs:,}, p = {p_value:.4g}</text>',
    ]
    for tick in ticks:
        y = y_position(float(tick))
        svg.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}"/>')
        svg.append(f'<text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end" font-size="13">{tick:.1f}</text>')
    svg.append(f'<rect x="{left}" y="{y_position(ci_high):.2f}" width="{plot_width}" height="{max(0, y_position(ci_low) - y_position(ci_high)):.2f}" fill="#C44E52" opacity="0.13"/>')
    svg.append(f'<line x1="{left}" y1="{y_position(0):.2f}" x2="{left + plot_width}" y2="{y_position(0):.2f}" stroke="#444" stroke-width="1.5" stroke-dasharray="7,6"/>')
    svg.append(f'<line x1="{left}" y1="{y_position(mean_difference):.2f}" x2="{left + plot_width}" y2="{y_position(mean_difference):.2f}" stroke="#C44E52" stroke-width="2.5"/>')
    for index, value in enumerate(ranked):
        svg.append(f'<circle cx="{x_position(index):.2f}" cy="{y_position(float(value)):.2f}" r="3.6" fill="#2878A8" opacity="0.68"/>')
    svg.extend(
        [
            f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}"/>',
            f'<line class="axis" x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}"/>',
            f'<text x="{left + plot_width / 2:.1f}" y="{height - 51}" text-anchor="middle" font-size="15">Countries/economies, ordered by paired difference</text>',
            f'<text transform="translate(25 {top + plot_height / 2:.1f}) rotate(-90)" text-anchor="middle" font-size="15">Difference in mean growth (percentage points)</text>',
            '<line x1="735" y1="601" x2="770" y2="601" stroke="#444" stroke-width="1.5" stroke-dasharray="7,6"/><text x="778" y="606" font-size="13">No difference</text>',
            '<line x1="890" y1="601" x2="925" y2="601" stroke="#C44E52" stroke-width="2.5"/><text x="933" y="606" font-size="13">Mean</text>',
            '<rect x="985" y="594" width="20" height="14" fill="#C44E52" opacity="0.18"/><text x="1011" y="606" font-size="13">95% CI</text>',
            '</svg>',
        ]
    )
    figure_path.write_text("\n".join(svg), encoding="utf-8")

    print(f"Input: {input_path.relative_to(ROOT)}")
    print(f"Country-years with both variables: {len(valid):,}")
    print(f"Country/economy pairs analyzed: {n_pairs:,}")
    print(f"Mean growth in low-rent years: {paired['low_rent_mean_gdp_per_capita_growth_pct'].mean():.4f}%")
    print(f"Mean growth in high-rent years: {paired['high_rent_mean_gdp_per_capita_growth_pct'].mean():.4f}%")
    print(f"Mean difference (high minus low): {mean_difference:.4f} percentage points")
    print(f"95% CI: [{ci_low:.4f}, {ci_high:.4f}], paired t p={p_value:.6g}")
    print(f"Wilcoxon sensitivity p={wilcoxon_p:.6g}")
    print(f"Summary: {summary_path.relative_to(ROOT)}")
    print(f"Country-level pairs: {paired_path.relative_to(ROOT)}")
    print(f"Report: {report_path.relative_to(ROOT)}")
    print(f"Figure: {figure_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
