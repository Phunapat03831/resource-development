from pathlib import Path
import re
import pandas as pd

FILE = Path("data/raw/adddata.xlsx")

if not FILE.exists():
    raise FileNotFoundError(
        f"ไม่พบไฟล์: {FILE.resolve()}\n"
        "ตรวจว่า adddata.xlsx อยู่ในโฟลเดอร์ data/raw/"
    )

try:
    excel = pd.ExcelFile(FILE)
except ImportError as e:
    raise SystemExit(
        "ยังเปิดไฟล์ Excel ไม่ได้ ติดตั้งไลบรารีด้วยคำสั่ง:\n"
        "python -m pip install openpyxl"
    ) from e

print(f"ไฟล์: {FILE.resolve()}")
print(f"ชีตที่พบ: {excel.sheet_names}")

for sheet in excel.sheet_names:
    print("\n" + "=" * 90)
    print(f"ชีต: {sheet}")

    # อ่านแบบยังไม่กำหนดหัวตาราง เพื่อค้นหาว่าหัวตารางเริ่มแถวไหน
    raw = pd.read_excel(FILE, sheet_name=sheet, header=None)

    header_row = None
    for i in range(min(len(raw), 20)):
        row_values = raw.iloc[i].astype(str).str.strip().str.lower().tolist()
        has_country_code = any("country code" in value for value in row_values)
        has_series = any("series name" in value for value in row_values)

        if has_country_code and has_series:
            header_row = i
            break

    if header_row is None:
        print("หาแถวหัวตารางแบบ WDI ไม่พบ")
        print("ตัวอย่างข้อมูล 8 แถวแรก:")
        print(raw.head(8).to_string(index=False, header=False))
        continue

    df = pd.read_excel(FILE, sheet_name=sheet, header=header_row)
    df.columns = [str(col).strip() for col in df.columns]

    print(f"แถวหัวตาราง: {header_row + 1}")
    print(f"จำนวนแถวข้อมูล: {len(df):,}")
    print("คอลัมน์:", list(df.columns))

    # แสดงตัวแปรและรหัสที่มีในไฟล์
    series_col = next(
        (col for col in df.columns if col.strip().lower() == "series name"),
        None
    )
    code_col = next(
        (col for col in df.columns if col.strip().lower() == "series code"),
        None
    )
    country_col = next(
        (col for col in df.columns if col.strip().lower() == "country code"),
        None
    )

    if series_col:
        print("\nตัวแปรที่พบ:")
        if code_col:
            series = (
                df[[series_col, code_col]]
                .dropna(subset=[series_col])
                .drop_duplicates()
            )
            print(series.to_string(index=False))
        else:
            print(df[series_col].dropna().drop_duplicates().to_string(index=False))

    # หาคอลัมน์ปี เช่น 2000 [YR2000]
    year_columns = [
        col for col in df.columns
        if re.search(r"(19|20)\d{2}", str(col))
    ]

    if year_columns:
        years = []
        for col in year_columns:
            match = re.search(r"(19|20)\d{2}", str(col))
            if match:
                years.append(int(match.group()))

        print(f"\nช่วงปี: {min(years)}–{max(years)}")
        print(f"จำนวนคอลัมน์ปี: {len(year_columns)}")
    else:
        print("\nไม่พบคอลัมน์ปี")

    if country_col:
        countries = df[country_col].dropna().astype(str).str.strip().nunique()
        print(f"จำนวน Country Code ที่ไม่ว่าง: {countries:,}")

    print("\nตัวอย่างข้อมูล 5 แถว:")
    print(df.head(5).to_string(index=False))