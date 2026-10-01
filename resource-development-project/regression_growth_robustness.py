from pathlib import Path
import warnings

import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "data" / "processed" / "resource_panel_all.csv"
RESULTS_DIR = ROOT / "data" / "processed" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COUNTRY = "Country Code"
YEAR = "Year"
Y = "gdp_per_capita_growth_pct"
RENT = "total_resource_rents_pct_gdp"
LAG_RENT = "resource_rents_pct_gdp_previous_year"


def estimate(data, model_name, predictor):
    formula = f'{Y} ~ {predictor} + C(Q("{COUNTRY}")) + C({YEAR})'

    # Country-clustered standard errors are used for all specifications.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = smf.ols(formula=formula, data=data).fit(
            cov_type="cluster",
            cov_kwds={"groups": data[COUNTRY]},
        )

    interval = result.conf_int().loc[predictor]
    row = {
        "model": model_name,
        "predictor": predictor,
        "coefficient": result.params[predictor],
        "clustered_standard_error": result.bse[predictor],
        "p_value": result.pvalues[predictor],
        "ci_95_low": interval.iloc[0],
        "ci_95_high": interval.iloc[1],
        "observations": int(result.nobs),
        "countries": int(data[COUNTRY].nunique()),
        "years": int(data[YEAR].nunique()),
        "r_squared_including_fixed_effects": result.rsquared,
        "country_fixed_effects": True,
        "year_fixed_effects": True,
        "standard_errors_clustered_by": "Country Code",
    }

    # Save only coefficient-level inference. The omnibus F-test over many
    # fixed effects can have a rank warning and is not the research question.
    report = (
        f"{model_name}\n"
        f"Formula: {formula}\n"
        f"Observations: {int(result.nobs):,}\n"
        f"Countries: {data[COUNTRY].nunique():,}\n"
        f"Years: {data[YEAR].nunique():,}\n"
        f"Coefficient: {result.params[predictor]:.6f}\n"
        f"Clustered standard error: {result.bse[predictor]:.6f}\n"
        f"p-value: {result.pvalues[predictor]:.6g}\n"
        f"95% confidence interval: [{interval.iloc[0]:.6f}, "
        f"{interval.iloc[1]:.6f}]\n"
        f"R-squared including fixed effects: {result.rsquared:.6f}\n"
    )
    if caught:
        report += "Fit warnings: " + " | ".join(
            str(item.message) for item in caught
        ) + "\n"

    return row, report


def main():
    if not INPUT_FILE.exists():
        raise SystemExit(f"ไม่พบไฟล์ข้อมูล: {INPUT_FILE}")

    data = pd.read_csv(INPUT_FILE)
    required = {COUNTRY, YEAR, Y, RENT}
    missing = required - set(data.columns)
    if missing:
        raise SystemExit(f"ไม่พบคอลัมน์ที่ต้องใช้: {sorted(missing)}")

    if data.duplicated([COUNTRY, YEAR]).any():
        raise SystemExit("พบ Country Code-Year ซ้ำใน resource_panel_all.csv")

    data[YEAR] = pd.to_numeric(data[YEAR], errors="coerce")
    data[Y] = pd.to_numeric(data[Y], errors="coerce")
    data[RENT] = pd.to_numeric(data[RENT], errors="coerce")
    data = data.dropna(subset=[COUNTRY, YEAR]).copy()
    data[YEAR] = data[YEAR].astype(int)

    # Match year t to the actual calendar year t-1 within the same country.
    # This avoids treating a multi-year gap as a one-year lag.
    previous = data[[COUNTRY, YEAR, RENT]].copy()
    previous[YEAR] = previous[YEAR] + 1
    previous = previous.rename(columns={RENT: LAG_RENT})
    data = data.merge(
        previous,
        on=[COUNTRY, YEAR],
        how="left",
        validate="one_to_one",
    )

    # Original same-year baseline uses every available Y and same-year rent.
    baseline = data.dropna(subset=[Y, RENT]).copy()

    # For a fair same-year vs lagged comparison, estimate both on exactly the
    # same observations that have outcome, current rent, and previous-year rent.
    common = data.dropna(subset=[Y, RENT, LAG_RENT]).copy()

    if baseline.empty or common.empty:
        raise SystemExit("ไม่มีแถวข้อมูลพอสำหรับประมาณ regression")

    specifications = [
        ("Same-year rents: full available sample", baseline, RENT),
        ("Same-year rents: common lag-comparison sample", common, RENT),
        ("Previous-year rents: common lag-comparison sample", common, LAG_RENT),
    ]

    rows = []
    reports = [
        "ผลหลัก: GDP per capita growth กับ Total natural resources rents",
        "Country and year fixed effects; standard errors clustered by country.",
        "โมเดลร่วมสมัยและโมเดล lag เปรียบเทียบกันบนตัวอย่างเดียวกัน.",
        "ผลเป็นความสัมพันธ์ทางสถิติ ไม่ใช่หลักฐานยืนยันเหตุและผล.\n",
    ]

    for model_name, sample, predictor in specifications:
        row, report = estimate(sample, model_name, predictor)
        rows.append(row)
        reports.append(report)
        print(
            f"{model_name}: {row['observations']:,} country-years, "
            f"{row['countries']:,} countries; "
            f"coefficient={row['coefficient']:.4f}, "
            f"p={row['p_value']:.4g}"
        )

    results_file = RESULTS_DIR / "growth_lag_robustness.csv"
    report_file = RESULTS_DIR / "growth_lag_robustness.txt"
    pd.DataFrame(rows).to_csv(
        results_file,
        index=False,
        encoding="utf-8-sig",
    )
    report_file.write_text("\n".join(reports), encoding="utf-8")

    print("\nเสร็จแล้ว")
    print(f"ตารางผล: {results_file}")
    print(f"รายงาน: {report_file}")
    print(
        "การตีความ: ค่าสัมประสิทธิ์แสดงความสัมพันธ์เมื่อ resource rents "
        "เพิ่มขึ้น 1 จุดเปอร์เซ็นต์ของ GDP โดยควบคุม fixed effects แล้ว"
    )


if __name__ == "__main__":
    main()
