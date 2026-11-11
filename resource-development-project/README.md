# คู่มือโครงงาน

โครงงานนี้เปรียบเทียบการเติบโตของ GDP ต่อหัวระหว่างปีที่ resource rents ต่ำกับสูง **ภายในประเทศเดิม** โดยใช้ข้อมูล World Development Indicators (WDI)

## ผลหลักที่ต้องรายงาน

ช่วงปีหลัก 2000–2021 ได้ 189 คู่ประเทศ/เขตเศรษฐกิจ ค่าเฉลี่ย GDP per capita growth ช่วง rents สูงมากกว่าช่วงต่ำเฉลี่ย 1.226 จุดเปอร์เซ็นต์, paired t-test: t(188) = 4.373, p = 0.000020, 95% CI [0.673, 1.779]. ผลตรวจสอบช่วงยาว 1970–2021 ให้ผลต่างเฉลี่ย +0.973 จุดเปอร์เซ็นต์, p = 0.000485; จำนวนคู่ยังเป็น 189

อ่าน [สรุปสำหรับนำเสนอ](docs/PRESENTATION_BRIEF.md) ก่อนใช้ตัวเลข และดู [คำอธิบายข้อมูล](docs/DATA_DICTIONARY.md) เพื่ออธิบายแหล่งที่มาและความหมายตัวแปร

ดาวน์โหลด [สไลด์นำเสนอภาษาไทย (PowerPoint)](docs/resource-rents-gdp-growth-presentation.pptx)

## ทำซ้ำการวิเคราะห์

จากโฟลเดอร์หลักของ repository ให้เปิด PowerShell แล้วรัน:

    cd resource-development-project
    python -m pip install -r requirements.txt
    python matched_pairs_period_sensitivity.py

สคริปต์อ่านไฟล์ `data/raw/wdi_growth_rents_1960_2025.csv` และรายชื่อหน่วยวิเคราะห์ `data/processed/country_list_to_review.csv` จากนั้นสร้างผลใน `data/processed/results/` ได้แก่ ตารางเปรียบเทียบสองช่วง ผลรายประเทศ และรายงานข้อความ

## โครงสร้างที่จำเป็น

- `data/raw/` — ไฟล์ WDI ต้นฉบับที่ใช้คำนวณ
- `data/processed/country_list_to_review.csv` — รายชื่อ 217 ประเทศ/เขตเศรษฐกิจที่ใช้คัดข้อมูล
- `data/processed/results/` — ตารางผลและกราฟสำหรับนำเสนอ
- สคริปต์วิเคราะห์หลัก: `matched_pairs_period_sensitivity.py`
- `docs/` — บันทึกสำหรับนำเสนอและคำอธิบายข้อมูล

## ข้อควรระวัง

paired test ใช้หนึ่งผลต่างต่อประเทศ จึงมี N = 189 คู่ ไม่ใช่จำนวนประเทศ–ปี การเปรียบเทียบนี้ไม่ได้ควบคุมเหตุการณ์เฉพาะปีหรือปัจจัยอื่นที่เปลี่ยนตามเวลา และไม่ใช่หลักฐานเชิงเหตุและผล
