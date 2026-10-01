from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent
file = root / "data" / "processed" / "resource_panel_all.csv"
df = pd.read_csv(file)

print(f"แถวทั้งหมด: {len(df):,}")
print(f"ประเทศ/เขตเศรษฐกิจ: {df['Country Code'].nunique()}")
print(f"ช่วงปี: {df['Year'].min()}–{df['Year'].max()}")

# ต้องไม่ซ้ำ: หนึ่งแถวต่อประเทศต่อปี
duplicates = df.duplicated(["Country Code", "Year"]).sum()
print(f"\nประเทศ-ปีซ้ำ: {duplicates}")
print("ผล:", "ผ่าน" if duplicates == 0 else "ตรวจซ้ำก่อน")

# เช็กว่ามีกลุ่มรวมที่รู้จักหลงเหลือไหม
aggregate_codes = {
    "AFE", "AFW", "ARB", "CSS", "CEB", "EAR", "EAS", "EAP", "TEA",
    "ECS", "ECA", "TEC", "EMU", "EUU", "FCS", "HIC", "HPC", "IBD",
    "IBT", "IDB", "IDX", "IDA", "LCN", "LAC", "TLA", "LDC", "LMY",
    "LIC", "LMC", "MEA", "TMN", "MNA", "MIC", "NAC", "OED", "OSS",
    "PSS", "PRE", "SST", "SAS", "TSA", "SSF", "TSS", "SSA", "LTE",
    "UMC", "WLD", "INX", "PST",
}
found = sorted(set(df["Country Code"].dropna()) & aggregate_codes)
print(f"\nรหัสกลุ่มรวมที่ยังพบ: {found if found else 'ไม่พบ'}")

# ค่าที่ควรอยู่ระหว่าง 0 ถึง 100
for col in [
    "poverty_gap_3usd_pct",
    "gini_index",
    "political_stability_score_0_100",
]:
    if col in df.columns:
        values = df[col].dropna()
        outside = ((values < 0) | (values > 100)).sum()
        print(f"{col}: ค่านอกช่วง 0–100 = {outside}")

# จำนวนข้อมูลของไฟล์แต่ละโมเดล
print("\nขนาดชุดข้อมูลสำหรับวิเคราะห์:")
for file in sorted((root / "data" / "processed").glob("model_*.csv")):
    model = pd.read_csv(file)
    print(f"{file.name}: {len(model):,} ประเทศ-ปี, "
          f"{model['Country Code'].nunique()} หน่วย")