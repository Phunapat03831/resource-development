from pathlib import Path
import re
import sys

import pandas as pd


# ใช้ไฟล์เดียวกับที่ตรวจดูแล้ว
ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "data" / "raw" / "data.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"
RESULTS_DIR = OUTPUT_DIR / "results"

START_YEAR = 2000
END_YEAR = 2021

# ตัวแปรจากไฟล์ WDI
SERIES = {
    "NY.GDP.TOTL.RT.ZS": "total_resource_rents_pct_gdp",
    "NY.GDP.NGAS.RT.ZS": "natural_gas_rents_pct_gdp",
    "NY.GDP.PETR.RT.ZS": "oil_rents_pct_gdp",
    "NY.GDP.COAL.RT.ZS": "coal_rents_pct_gdp",
    "NY.GDP.MINR.RT.ZS": "mineral_rents_pct_gdp",
    "NY.GDP.FRST.RT.ZS": "forest_rents_pct_gdp",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "NY.GDP.PCAP.KD.ZG": "gdp_per_capita_growth_pct",
    "SI.POV.GAPS": "poverty_gap_3usd_pct",
    "SI.POV.GINI": "gini_index",
    "GOV_WGI_PV_SC": "political_stability_score_0_100",
}

# รหัสกลุ่มภูมิภาค กลุ่มรายได้ และยอดรวมที่พบได้ในไฟล์ World Bank
AGGREGATE_CODES = {
    "AFE", "AFW", "ARB", "CSS", "CEB", "EAR", "EAS", "EAP", "TEA",
    "ECS", "ECA", "TEC", "EMU", "EUU", "FCS", "HIC", "HPC", "IBD",
    "IBT", "IDB", "IDX", "IDA", "LCN", "LAC", "TLA", "LDC", "LMY",
    "LIC", "LMC", "MEA", "TMN", "MNA", "MIC", "NAC", "OED", "OSS",
    "PSS", "PRE", "SST", "SAS", "TSA", "SSF", "TSS", "SSA", "LTE",
    "UMC", "WLD",
    "INX", "PST",  # Not classified, Post-demographic dividend
}


def stop(message):
    print(f"\nERROR: {message}")
    sys.exit(1)


def main():
    if not INPUT_FILE.exists():
        stop(
            f"ไม่พบไฟล์ {INPUT_FILE}\n"
            "ตรวจว่าได้วาง data.xlsx ไว้ใน data/raw/ แล้ว"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"กำลังอ่าน: {INPUT_FILE}")
    try:
        df = pd.read_excel(INPUT_FILE, sheet_name="data")
    except Exception as error:
        stop(f"เปิดไฟล์ Excel ไม่สำเร็จ: {error}")

    required_columns = {
        "Series Name",
        "Series Code",
        "Country Name",
        "Country Code",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        stop(f"ไม่พบคอลัมน์ที่ต้องใช้: {sorted(missing_columns)}")

    # หาเฉพาะคอลัมน์ปี เช่น 2000 [YR2000]
    year_columns = {}
    for column in df.columns:
        match = re.match(r"^\s*(\d{4})\s*\[YR\d{4}\]\s*$", str(column))
        if match:
            year = int(match.group(1))
            if START_YEAR <= year <= END_YEAR:
                year_columns[column] = year

    if not year_columns:
        stop(f"ไม่พบคอลัมน์ปีในช่วง {START_YEAR}–{END_YEAR}")

    # เก็บเฉพาะแถวตัวแปรที่ต้องการ และตัดบรรทัดหมายเหตุท้ายไฟล์
    df["Series Code"] = df["Series Code"].astype("string").str.strip()
    df["Country Code"] = df["Country Code"].astype("string").str.strip()

    wanted_codes = set(SERIES)
    selected = df[
        df["Series Code"].isin(wanted_codes)
        & df["Country Code"].notna()
    ].copy()

    found_codes = set(selected["Series Code"].dropna())
    missing_series = wanted_codes - found_codes
    if missing_series:
        print("คำเตือน: ไม่พบ series code เหล่านี้ในไฟล์:")
        for code in sorted(missing_series):
            print(f"  - {code} ({SERIES[code]})")

    if selected.empty:
        stop("ไม่พบแถวข้อมูลของตัวแปรที่ต้องการ")

    # ตัดแถวภูมิภาค/กลุ่มรายได้/ยอดรวมออก
    selected["Country Code"] = selected["Country Code"].str.upper()
    aggregate_rows = selected[
        selected["Country Code"].isin(AGGREGATE_CODES)
    ].copy()
    selected = selected[
        ~selected["Country Code"].isin(AGGREGATE_CODES)
    ].copy()

    aggregate_rows[
        ["Country Name", "Country Code", "Series Name", "Series Code"]
    ].drop_duplicates().to_csv(
        OUTPUT_DIR / "aggregate_rows_removed.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print(f"แถวข้อมูลตัวแปรที่เลือก: {len(selected):,}")
    print(f"แถวกลุ่มรวมที่ตัดออก: {len(aggregate_rows):,}")

    # แปลงข้อมูลจากคอลัมน์ปี ให้เป็นแถวละประเทศ-ปี-ตัวแปร
    id_columns = [
        "Country Name",
        "Country Code",
        "Series Name",
        "Series Code",
    ]
    long = selected[id_columns + list(year_columns)].melt(
        id_vars=id_columns,
        var_name="year_column",
        value_name="value",
    )
    long["Year"] = long["year_column"].map(year_columns)
    long["Value"] = pd.to_numeric(long["value"], errors="coerce")

    # ตรวจประเทศ-ปี-ตัวแปรซ้ำก่อนจัดเป็นตารางกว้าง
    duplicate_mask = long.duplicated(
        subset=["Country Code", "Year", "Series Code"],
        keep=False,
    )
    if duplicate_mask.any():
        duplicates = long.loc[
            duplicate_mask,
            ["Country Name", "Country Code", "Year", "Series Code"],
        ].drop_duplicates()
        duplicates.to_csv(
            OUTPUT_DIR / "duplicate_country_year_series.csv",
            index=False,
            encoding="utf-8-sig",
        )
        stop(
            "พบประเทศ-ปี-ตัวแปรซ้ำ "
            "รายละเอียดอยู่ใน duplicate_country_year_series.csv"
        )

    # จัดข้อมูลเป็นหนึ่งแถวต่อประเทศ-ปี และหนึ่งคอลัมน์ต่อตัวแปร
    wide = long.pivot(
        index=["Country Code", "Year"],
        columns="Series Code",
        values="Value",
    ).reset_index()
    wide.columns.name = None

    # ให้ทุกตัวแปรที่เลือกมีคอลัมน์ แม้บางตัวจะไม่มีข้อมูลเลย
    for code in SERIES:
        if code not in wide.columns:
            wide[code] = pd.NA

    # เติมชื่อประเทศจากข้อมูลต้นทาง
    country_names = (
        selected[["Country Code", "Country Name"]]
        .drop_duplicates(subset="Country Code")
        .set_index("Country Code")["Country Name"]
    )
    wide.insert(
        1,
        "Country Name",
        wide["Country Code"].map(country_names),
    )

    # เปลี่ยนรหัส series เป็นชื่อคอลัมน์อ่านง่าย
    wide = wide.rename(columns=SERIES)
    wide = wide.sort_values(["Country Name", "Year"]).reset_index(drop=True)

    # เก็บชุดข้อมูลรวม โดยยังไม่ตัดแถวที่มี missing
    panel_file = OUTPUT_DIR / "resource_panel_all.csv"
    wide.to_csv(panel_file, index=False, encoding="utf-8-sig")

    # สรุปจำนวนข้อมูลที่มีและหายไปแยกตามตัวแปร
    variables = list(SERIES.values())
    availability_rows = []

    for variable in variables:
        present = wide[variable].notna()
        available = wide.loc[present]

        availability_rows.append({
            "Variable": variable,
            "Non-missing country-years": int(present.sum()),
            "Missing country-years": int(wide[variable].isna().sum()),
            "Countries with data": int(available["Country Code"].nunique()),
            "First year with data": (
                int(available["Year"].min()) if not available.empty else None
            ),
            "Last year with data": (
                int(available["Year"].max()) if not available.empty else None
            ),
        })

    availability = pd.DataFrame(availability_rows)
    availability.to_csv(
        OUTPUT_DIR / "data_availability.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # รายชื่อประเทศที่เหลือหลังตัดแถวกลุ่มรวม
    wide[["Country Code", "Country Name"]].drop_duplicates().sort_values(
        "Country Name"
    ).to_csv(
        OUTPUT_DIR / "country_list_to_review.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # สถิติเบื้องต้น คำนวณจากค่าที่มีจริงของแต่ละตัวแปร
    descriptive = wide[variables].describe().T
    descriptive.to_csv(
        RESULTS_DIR / "descriptive_statistics.csv",
        encoding="utf-8-sig",
    )

    # สร้างชุดข้อมูลแยกตามผลลัพธ์
    # แต่ละไฟล์ตัดเฉพาะแถวที่ขาดในตัวแปรผลลัพธ์และ total resource rents
    outcomes = {
        "gdp_growth": "gdp_growth_pct",
        "gdp_per_capita_growth": "gdp_per_capita_growth_pct",
        "poverty_gap": "poverty_gap_3usd_pct",
        "gini": "gini_index",
        "political_stability": "political_stability_score_0_100",
    }

    for model_name, outcome in outcomes.items():
        model_data = wide.dropna(
            subset=["total_resource_rents_pct_gdp", outcome]
        ).copy()

        model_data.to_csv(
            OUTPUT_DIR / f"model_{model_name}.csv",
            index=False,
            encoding="utf-8-sig",
        )

        print(
            f"model_{model_name}.csv: "
            f"{len(model_data):,} country-years, "
            f"{model_data['Country Code'].nunique():,} countries"
        )

    print("\nเสร็จแล้ว")
    print(f"ชุดข้อมูลรวม: {panel_file}")
    print(f"รายงานข้อมูลขาด: {OUTPUT_DIR / 'data_availability.csv'}")
    print(f"รายชื่อประเทศสำหรับตรวจ: {OUTPUT_DIR / 'country_list_to_review.csv'}")
    print(f"ผลลัพธ์อื่น ๆ อยู่ใน: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()