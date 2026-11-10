# ไฟล์ที่ใช้และผลวิเคราะห์

- `country_list_to_review.csv` — รายชื่อ 217 ประเทศ/เขตเศรษฐกิจที่กำหนดขอบเขตการวิเคราะห์
- `results/matched_pairs_period_comparison.csv` — ตารางสถิติรวมของช่วงหลัก 2000–2021 และช่วงตรวจสอบยาว 1970–2021
- `results/matched_pairs_period_country_results.csv` — ค่า rents จุดตัด ค่าเฉลี่ย growth และผลต่างของแต่ละหน่วยในแต่ละช่วง
- `results/matched_pairs_growth_difference.svg` — กราฟผลต่างรายประเทศสำหรับช่วงหลัก 2000–2021
- `results/matched_pairs_period_sensitivity_report.txt` — สร้างโดยสคริปต์เมื่อต้องการรายงานข้อความอีกครั้ง

รัน `python matched_pairs_period_sensitivity.py` จากโฟลเดอร์หลักของโครงงานเพื่อสร้างตารางและรายงานใหม่
