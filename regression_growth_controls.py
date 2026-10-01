from pathlib import Path
import math

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "data" / "processed" / "resource_panel_with_controls.csv"
RESULTS_DIR = ROOT / "data" / "processed" / "results"

COUNTRY = "Country Code"
YEAR = "Year"
Y = "gdp_per_capita_growth_pct"
RENT = "total_resource_rents_pct_gdp"
LAG_RENT = "resource_rents_pct_gdp_previous_year"
LAG_INCOME = "log_gdp_per_capita_previous_year"
POP_GROWTH = "population_growth_pct"
INVESTMENT = "gross_capital_formation_pct_gdp"
TRADE = "trade_pct_gdp"


def estimate(frame, model_name, rhs):
    terms = list(rhs)
    # Explicit country/year dummies implement two-way fixed effects.
    country_dummies = pd.get_dummies(frame[COUNTRY], drop_first=True, dtype=float)
    year_dummies = pd.get_dummies(frame[YEAR], drop_first=True, dtype=float)
    x = np.column_stack([
        np.ones(len(frame)),
        frame[terms].to_numpy(dtype=float),
        country_dummies.to_numpy(dtype=float),
        year_dummies.to_numpy(dtype=float),
    ])
    y = frame[Y].to_numpy(dtype=float)
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank < x.shape[1]:
        raise ValueError(f"แบบจำลอง {model_name} มีตัวแปรซ้ำซ้อนจนเมทริกซ์ไม่ full rank")
    residual = y - x @ beta
    n, k = x.shape
    bread = np.linalg.inv(x.T @ x)

    # Country-clustered sandwich covariance with the usual finite-sample correction.
    meat = np.zeros((k, k), dtype=float)
    groups = frame[COUNTRY].to_numpy()
    for group in pd.unique(groups):
        selected = groups == group
        score = x[selected].T @ residual[selected]
        meat += np.outer(score, score)
    cluster_count = frame[COUNTRY].nunique()
    correction = (cluster_count / (cluster_count - 1)) * ((n - 1) / (n - k))
    covariance = bread @ meat @ bread * correction
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0))
    mean_y = y.mean()
    r_squared = 1 - (residual @ residual) / np.sum((y - mean_y) ** 2)
    term_index = {term: 1 + i for i, term in enumerate(terms)}
    rows = []
    for term in terms:
        j = term_index[term]
        coefficient = beta[j]
        se = standard_errors[j]
        z = coefficient / se if se else np.nan
        p_value = math.erfc(abs(z) / math.sqrt(2)) if np.isfinite(z) else np.nan
        rows.append({
            "model": model_name,
            "variable": term,
            "coefficient": coefficient,
            "clustered_standard_error": se,
            "p_value": p_value,
            "ci_95_low": coefficient - 1.96 * se,
            "ci_95_high": coefficient + 1.96 * se,
            "observations": n,
            "countries": int(frame[COUNTRY].nunique()),
            "first_year": int(frame[YEAR].min()),
            "last_year": int(frame[YEAR].max()),
            "r_squared_including_fixed_effects": r_squared,
            "country_fixed_effects": True,
            "year_fixed_effects": True,
            "standard_errors_clustered_by": COUNTRY,
        })
    return rows


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_FILE.exists():
        raise SystemExit(f"ไม่พบไฟล์ {INPUT_FILE}; รัน merge_additional_wdi.py ก่อน")

    data = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    required = {
        COUNTRY, YEAR, Y, RENT, POP_GROWTH, INVESTMENT, TRADE,
        "gdp_per_capita_constant_2015_usd",
    }
    missing = required - set(data.columns)
    if missing:
        raise SystemExit(f"ขาดคอลัมน์ที่ต้องใช้: {sorted(missing)}")
    if data.duplicated([COUNTRY, YEAR]).any():
        raise SystemExit("พบ Country Code-Year ซ้ำ")

    data[YEAR] = pd.to_numeric(data[YEAR], errors="coerce")
    numeric = [
        Y, RENT, POP_GROWTH, INVESTMENT, TRADE,
        "gdp_per_capita_constant_2015_usd",
    ]
    for col in numeric:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=[COUNTRY, YEAR]).copy()
    data[YEAR] = data[YEAR].astype(int)

    # Attach prior-year GDP per capita only when the preceding calendar year exists.
    income_lag = data[[COUNTRY, YEAR, "gdp_per_capita_constant_2015_usd"]].copy()
    income_lag[YEAR] += 1
    income_lag = income_lag.rename(columns={
        "gdp_per_capita_constant_2015_usd": "gdp_per_capita_previous_year"
    })
    data = data.merge(
        income_lag, on=[COUNTRY, YEAR], how="left", validate="one_to_one"
    )
    data[LAG_INCOME] = np.where(
        data["gdp_per_capita_previous_year"] > 0,
        np.log(data["gdp_per_capita_previous_year"]),
        np.nan,
    )

    # Exact prior-calendar-year resource rents, avoiding gaps treated as one-year lags.
    lag = data[[COUNTRY, YEAR, RENT]].copy()
    lag[YEAR] += 1
    lag = lag.rename(columns={RENT: LAG_RENT})
    data = data.merge(lag, on=[COUNTRY, YEAR], how="left", validate="one_to_one")

    core_fields = [Y, RENT, LAG_INCOME, POP_GROWTH]
    core = data.dropna(subset=core_fields).copy()
    expanded_fields = core_fields + [INVESTMENT, TRADE]
    expanded = data.dropna(subset=expanded_fields).copy()
    lag_common_fields = core_fields + [LAG_RENT]
    lag_common = data.dropna(subset=lag_common_fields).copy()

    if core.empty or expanded.empty or lag_common.empty:
        raise SystemExit("ข้อมูลไม่พอสำหรับแบบจำลองควบคุมอย่างน้อยหนึ่งชุด")

    specifications = [
        ("Baseline on core-control sample", core, [RENT]),
        ("Core controls: lagged log GDP per capita + population growth", core,
         [RENT, LAG_INCOME, POP_GROWTH]),
        ("Baseline on expanded-control sample", expanded, [RENT]),
        ("Core controls on expanded-control sample", expanded,
         [RENT, LAG_INCOME, POP_GROWTH]),
        ("Expanded controls: core + investment + trade", expanded,
         [RENT, LAG_INCOME, POP_GROWTH, INVESTMENT, TRADE]),
        ("Same-year rents on lag-comparison sample", lag_common,
         [RENT, LAG_INCOME, POP_GROWTH]),
        ("Previous-year rents on lag-comparison sample", lag_common,
         [LAG_RENT, LAG_INCOME, POP_GROWTH]),
    ]

    output = []
    for name, sample, rhs in specifications:
        output.extend(estimate(sample, name, rhs))

    result_df = pd.DataFrame(output)
    csv_path = RESULTS_DIR / "growth_control_regression_coefficients.csv"
    txt_path = RESULTS_DIR / "growth_control_regression_summary.txt"
    result_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    key = result_df[result_df["variable"].isin([RENT, LAG_RENT])]
    lines = [
        "GDP per capita growth regressions with country and year fixed effects",
        "Standard errors are clustered by country.",
        "Coefficients are within-country associations conditional on included variables.",
        "They are not causal effects.",
        "Investment and trade are treated as supplementary expanded controls because they may also be channels through which rents relate to growth.",
        "",
    ]
    for _, row in key.iterrows():
        lines.append(
            f"{row['model']} | {row['variable']}: "
            f"b={row['coefficient']:.5f}, SE={row['clustered_standard_error']:.5f}, "
            f"p={row['p_value']:.5g}, 95% CI=[{row['ci_95_low']:.5f}, "
            f"{row['ci_95_high']:.5f}], n={row['observations']:,}, "
            f"countries={row['countries']:,}, "
            f"years={row['first_year']}–{row['last_year']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("ตัวแปร resource rents ในแบบจำลองควบคุม:")
    print(key[["model", "variable", "coefficient", "clustered_standard_error",
              "p_value", "ci_95_low", "ci_95_high", "observations", "countries"]]
          .to_string(index=False))
    print("\nผลลัพธ์:")
    print(csv_path)
    print(txt_path)


if __name__ == "__main__":
    main()
