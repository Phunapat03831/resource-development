from pathlib import Path
import warnings

import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parent
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = PROCESSED_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RESOURCE_VARIABLE = "total_resource_rents_pct_gdp"

# Each outcome is estimated separately because data coverage differs by variable.
MODELS = {
    "GDP growth": {
        "file": "model_gdp_growth.csv",
        "outcome": "gdp_growth_pct",
    },
    "GDP per capita growth": {
        "file": "model_gdp_per_capita_growth.csv",
        "outcome": "gdp_per_capita_growth_pct",
    },
    "Poverty gap": {
        "file": "model_poverty_gap.csv",
        "outcome": "poverty_gap_3usd_pct",
    },
    "Income inequality (Gini)": {
        "file": "model_gini.csv",
        "outcome": "gini_index",
    },
    "Political stability": {
        "file": "model_political_stability.csv",
        "outcome": "political_stability_score_0_100",
    },
}


def main():
    rows = []
    report_sections = []

    for model_name, spec in MODELS.items():
        input_file = PROCESSED_DIR / spec["file"]
        outcome = spec["outcome"]

        if not input_file.exists():
            print(f"ข้าม {model_name}: ไม่พบไฟล์ {input_file.name}")
            continue

        data = pd.read_csv(input_file)
        needed = [
            "Country Code",
            "Year",
            RESOURCE_VARIABLE,
            outcome,
        ]
        missing = [column for column in needed if column not in data.columns]
        if missing:
            print(f"ข้าม {model_name}: ไม่พบคอลัมน์ {missing}")
            continue

        data = data[needed].copy()
        data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
        data[RESOURCE_VARIABLE] = pd.to_numeric(
            data[RESOURCE_VARIABLE], errors="coerce"
        )
        data[outcome] = pd.to_numeric(data[outcome], errors="coerce")
        data = data.dropna(subset=needed)

        # Avoid attempting country fixed effects for countries with no variation
        # in the outcome/rent over time; statsmodels handles the FE coding.
        data["Country Code"] = data["Country Code"].astype(str)
        data["Year"] = data["Year"].astype(int)

        formula = (
            f"{outcome} ~ {RESOURCE_VARIABLE} "
            '+ C(Q("Country Code")) + C(Year)'
        )

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = smf.ols(formula=formula, data=data).fit(
                cov_type="cluster",
                cov_kwds={"groups": data["Country Code"]},
            )

        term = RESOURCE_VARIABLE
        ci = result.conf_int().loc[term]
        rows.append({
            "model": model_name,
            "outcome_variable": outcome,
            "predictor": RESOURCE_VARIABLE,
            "coefficient": result.params[term],
            "clustered_standard_error": result.bse[term],
            "p_value": result.pvalues[term],
            "ci_95_low": ci.iloc[0],
            "ci_95_high": ci.iloc[1],
            "observations": int(result.nobs),
            "countries": int(data["Country Code"].nunique()),
            "years": int(data["Year"].nunique()),
            "r_squared_including_fixed_effects": result.rsquared,
        })

        report_sections.append(
            f"\n{'=' * 88}\n"
            f"{model_name}\n"
            f"Outcome: {outcome}\n"
            f"Predictor: {RESOURCE_VARIABLE}\n"
            "Country fixed effects: Yes\n"
            "Year fixed effects: Yes\n"
            "Standard errors: Clustered by country\n"
            f"Observations: {int(result.nobs):,}\n"
            f"Countries: {data['Country Code'].nunique():,}\n"
            f"Years: {data['Year'].nunique():,}\n"
            f"Coefficient on resource rents: {result.params[term]:.6f}\n"
            f"Clustered standard error: {result.bse[term]:.6f}\n"
            f"p-value: {result.pvalues[term]:.6g}\n"
            f"95% confidence interval: [{ci.iloc[0]:.6f}, {ci.iloc[1]:.6f}]\n"
            f"R-squared including fixed effects: {result.rsquared:.6f}\n\n"
            f"{result.summary().as_text()}\n"
            + (
                "Warnings:\n" + "\n".join(str(w.message) for w in caught) + "\n"
                if caught else ""
            )
        )

        print(
            f"{model_name}: {int(result.nobs):,} country-years, "
            f"{data['Country Code'].nunique():,} countries, "
            f"coefficient={result.params[term]:.4f}, "
            f"p={result.pvalues[term]:.4g}"
        )

    if not rows:
        raise SystemExit(
            "ไม่มีโมเดลที่รันได้ ตรวจชื่อไฟล์และคอลัมน์ใน data/processed/"
        )

    coefficients = pd.DataFrame(rows)
    coefficients.to_csv(
        RESULTS_DIR / "resource_curse_regression_coefficients.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (RESULTS_DIR / "resource_curse_regression_summaries.txt").write_text(
        "\n".join(report_sections),
        encoding="utf-8",
    )

    print("\nRegression เสร็จแล้ว")
    print(f"ตารางผล: {RESULTS_DIR / 'resource_curse_regression_coefficients.csv'}")
    print(f"รายงานโมเดล: {RESULTS_DIR / 'resource_curse_regression_summaries.txt'}")
    print(
        "\nการตีความ: ค่าสัมประสิทธิ์คือความสัมพันธ์กับการเพิ่มขึ้น 1 จุดเปอร์เซ็นต์ "
        "ของ resource rents (% GDP) โดยควบคุม fixed effects ของประเทศและปีแล้ว; "
        "ไม่ใช่หลักฐานเชิงเหตุและผล"
    )


if __name__ == "__main__":
    main()
