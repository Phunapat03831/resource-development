from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
PANEL_FILE = ROOT / "data" / "processed" / "resource_panel_all.csv"
ADDDATA_FILE = ROOT / "data" / "raw" / "adddata.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"

START_YEAR = 2000
END_YEAR = 2021

# WDI series codes from adddata.xlsx
ADDITIONAL_SERIES = {
    "NY.GDP.PCAP.KD": "gdp_per_capita_constant_2015_usd",
    "SP.POP.GROW": "population_growth_pct",
    "NE.GDI.TOTL.ZS": "gross_capital_formation_pct_gdp",
    "NE.TRD.GNFS.ZS": "trade_pct_gdp",
}

# Aggregate regions, income groups, and World Bank totals; not individual economies.
AGGREGATE_CODES = {
    "AFE", "AFW", "ARB", "CSS", "CEB", "EAR", "EAS", "EAP", "TEA",
    "ECS", "ECA", "TEC", "EMU", "EUU", "FCS", "HIC", "HPC", "IBD",
    "IBT", "IDB", "IDX", "IDA", "LCN", "LAC", "TLA", "LDC", "LMY",
    "LIC", "LMC", "MEA", "TMN", "MNA", "MIC", "NAC", "OED", "OSS",
    "PSS", "PRE", "SST", "SAS", "TSA", "SSF", "TSS", "SSA", "LTE",
    "UMC", "WLD", "INX", "PST",
}


def stop(message):
    raise SystemExit(f"\nERROR: {message}")


def find_wdi_header(raw):
    for row_number in range(min(len(raw), 20)):
        values = raw.iloc[row_number].astype(str).str.strip().str.lower()
        if "country code" in values.values and "series code" in values.values:
            return row_number
    return None


def read_additional_data():
    if not ADDDATA_FILE.exists():
        stop(f"ไม่พบไฟล์ {ADDDATA_FILE}")

    try:
        book = pd.ExcelFile(ADDDATA_FILE)
    except Exception as error:
        stop(f"เปิด adddata.xlsx ไม่สำเร็จ: {error}")

    selected_parts = []
    for sheet in book.sheet_names:
        raw = pd.read_excel(ADDDATA_FILE, sheet_name=sheet, header=None)
        header_row = find_wdi_header(raw)
        if header_row is None:
            continue

        frame = pd.read_excel(ADDDATA_FILE, sheet_name=sheet, header=header_row)
        frame.columns = [str(column).strip() for column in frame.columns]
        required = {"Country Name", "Country Code", "Series Code"}
        if not required.issubset(frame.columns):
            continue

        years = {}
        for column in frame.columns:
            match = re.match(r"^\s*(\d{4})\s*\[YR\d{4}\]\s*$", str(column))
            if match:
                year = int(match.group(1))
                if START_YEAR <= year <= END_YEAR:
                    years[column] = year
        if not years:
            continue

        frame["Series Code"] = frame["Series Code"].astype("string").str.strip()
        frame["Country Code"] = (
            frame["Country Code"].astype("string").str.strip().str.upper()
        )
        frame = frame[
            frame["Series Code"].isin(ADDITIONAL_SERIES)
            & frame["Country Code"].notna()
            & ~frame["Country Code"].isin(AGGREGATE_CODES)
        ].copy()
        if frame.empty:
            continue

        long = frame[
            ["Country Name", "Country Code", "Series Code"] + list(years)
        ].melt(
            id_vars=["Country Name", "Country Code", "Series Code"],
            var_name="year_column",
            value_name="value",
        )
        long["Year"] = long["year_column"].map(years).astype(int)
        long["value"] = pd.to_numeric(long["value"], errors="coerce")
        selected_parts.append(long)

    if not selected_parts:
        stop("ไม่พบตาราง WDI ที่มีตัวแปรเป้าหมายใน adddata.xlsx")

    long = pd.concat(selected_parts, ignore_index=True)
    duplicated = long.duplicated(["Country Code", "Year", "Series Code"], keep=False)
    if duplicated.any():
        detail = long.loc[
            duplicated, ["Country Name", "Country Code", "Year", "Series Code"]
        ].drop_duplicates()
        detail.to_csv(
            OUTPUT_DIR / "adddata_duplicates.csv", index=False, encoding="utf-8-sig"
        )
        stop("พบประเทศ-ปี-ตัวแปรซ้ำ; รายละเอียดอยู่ใน adddata_duplicates.csv")

    missing_codes = set(ADDITIONAL_SERIES) - set(long["Series Code"].dropna())
    if missing_codes:
        stop(f"ไม่พบ WDI series code: {sorted(missing_codes)}")

    wide = long.pivot(
        index=["Country Code", "Year"], columns="Series Code", values="value"
    ).reset_index()
    wide.columns.name = None
    names = (
        long[["Country Code", "Country Name"]]
        .drop_duplicates("Country Code")
        .set_index("Country Code")["Country Name"]
    )
    wide.insert(1, "Country Name_adddata", wide["Country Code"].map(names))
    wide = wide.rename(columns=ADDITIONAL_SERIES)
    return wide


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not PANEL_FILE.exists():
        stop(f"ไม่พบชุดข้อมูลเดิม {PANEL_FILE}; รัน prepare_resource_data.py ก่อน")

    panel = pd.read_csv(PANEL_FILE, encoding="utf-8-sig")
    required = {"Country Code", "Country Name", "Year", "gdp_per_capita_growth_pct"}
    missing = required - set(panel.columns)
    if missing:
        stop(f"คอลัมน์ใน resource_panel_all.csv ไม่ครบ: {sorted(missing)}")

    panel["Country Code"] = panel["Country Code"].astype("string").str.strip().str.upper()
    panel["Year"] = pd.to_numeric(panel["Year"], errors="coerce")
    panel = panel.dropna(subset=["Country Code", "Year"]).copy()
    panel["Year"] = panel["Year"].astype(int)
    panel = panel[~panel["Country Code"].isin(AGGREGATE_CODES)].copy()

    if panel.duplicated(["Country Code", "Year"]).any():
        stop("พบ Country Code-Year ซ้ำใน resource_panel_all.csv")

    additional = read_additional_data()
    print(f"ข้อมูลเดิม: {len(panel):,} country-years, {panel['Country Code'].nunique():,} หน่วย")
    print(
        f"ข้อมูล adddata หลังตัดกลุ่มรวม: {len(additional):,} country-years, "
        f"{additional['Country Code'].nunique():,} หน่วย"
    )

    merged = panel.merge(
        additional,
        on=["Country Code", "Year"],
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    merged["Country Name"] = merged["Country Name"].combine_first(
        merged["Country Name_adddata"]
    )
    merged = merged.drop(columns=["Country Name_adddata", "_merge"])
    merged = merged.sort_values(["Country Name", "Year"]).reset_index(drop=True)

    panel_out = OUTPUT_DIR / "resource_panel_with_controls.csv"
    merged.to_csv(panel_out, index=False, encoding="utf-8-sig")

    extra_vars = list(ADDITIONAL_SERIES.values())
    availability = []
    for variable in extra_vars:
        available = merged[variable].notna()
        rows = merged.loc[available]
        availability.append({
            "Variable": variable,
            "Non-missing country-years": int(available.sum()),
            "Missing country-years": int(merged[variable].isna().sum()),
            "Countries with data": int(rows["Country Code"].nunique()),
            "First year with data": int(rows["Year"].min()) if len(rows) else None,
            "Last year with data": int(rows["Year"].max()) if len(rows) else None,
        })
    availability_file = OUTPUT_DIR / "additional_data_availability.csv"
    pd.DataFrame(availability).to_csv(
        availability_file, index=False, encoding="utf-8-sig"
    )

    # Exact-calendar-year lag of GDP per capita, then natural log.
    lag = merged[["Country Code", "Year", "gdp_per_capita_constant_2015_usd"]].copy()
    lag["Year"] += 1
    lag = lag.rename(columns={
        "gdp_per_capita_constant_2015_usd": "gdp_per_capita_previous_year"
    })
    merged = merged.merge(lag, on=["Country Code", "Year"], how="left", validate="one_to_one")
    merged["log_gdp_per_capita_previous_year"] = np.where(
        merged["gdp_per_capita_previous_year"] > 0,
        np.log(merged["gdp_per_capita_previous_year"]),
        np.nan,
    )

    # Main controlled sample: lagged income and population growth.
    core_columns = [
        "gdp_per_capita_growth_pct",
        "total_resource_rents_pct_gdp",
        "log_gdp_per_capita_previous_year",
        "population_growth_pct",
    ]
    core = merged.dropna(subset=core_columns).copy()
    core_file = OUTPUT_DIR / "model_gdp_per_capita_growth_core_controls.csv"
    core.to_csv(core_file, index=False, encoding="utf-8-sig")

    # Expanded sensitivity sample adds investment and trade; expected to be smaller.
    expanded_columns = core_columns + [
        "gross_capital_formation_pct_gdp",
        "trade_pct_gdp",
    ]
    expanded = merged.dropna(subset=expanded_columns).copy()
    expanded_file = OUTPUT_DIR / "model_gdp_per_capita_growth_expanded_controls.csv"
    expanded.to_csv(expanded_file, index=False, encoding="utf-8-sig")

    print("\nความครอบคลุมของตัวแปรใหม่:")
    print(pd.DataFrame(availability).to_string(index=False))
    print("\nชุดข้อมูลควบคุมสำหรับการวิเคราะห์:")
    for label, frame, path in [
        ("Core controls", core, core_file),
        ("Expanded controls", expanded, expanded_file),
    ]:
        years = frame["Year"]
        print(
            f"{label}: {len(frame):,} country-years, "
            f"{frame['Country Code'].nunique():,} หน่วย, "
            f"ปี {int(years.min()) if len(years) else 'ไม่มี'}–"
            f"{int(years.max()) if len(years) else 'ไม่มี'}"
        )
        print(f"  {path}")

    print("\nรวมข้อมูลเสร็จแล้ว")
    print(f"ชุดข้อมูลรวม: {panel_out}")
    print(f"รายงานข้อมูลตัวแปรใหม่: {availability_file}")


if __name__ == "__main__":
    main()
