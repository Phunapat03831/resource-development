import pandas as pd

file = "data/raw/data.xlsx"
df = pd.read_excel(file, sheet_name="data")

print("ขนาดตาราง:", df.shape)
print("\nตัวแปรทั้งหมดที่พบ:")
print(
    df[["Series Name", "Series Code"]]
    .drop_duplicates()
    .to_string(index=False)
)