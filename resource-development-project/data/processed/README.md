# ชุดข้อมูลประมวลผล

ไฟล์เหล่านี้สร้างจาก workbook ต้นทางใน data/raw/ ด้วยสคริปต์ในโฟลเดอร์หลัก

## ไฟล์ที่ใช้ทำงานหลัก

- resource_panel_all.csv — panel รวมตัวแปรหลักและตัวแปรเสริมหลังจัดรูปแบบและตัดกลุ่มรวม
- resource_panel_with_controls.csv — panel ที่รวมตัวแปรควบคุมเพิ่มเติมด้วย

## ผล matched pairs ที่ควรดูก่อน

อยู่ใน results/:

- matched_pairs_summary.csv — ผลรวมและสถิติทดสอบ
- matched_pairs_country_results.csv — ค่าเฉลี่ยกลุ่มต่ำ/สูงและผลต่างของแต่ละประเทศ
- matched_pairs_country_year_groups.csv — ปีที่ถูกจัดเป็นกลุ่มต่ำ/กลาง/สูง
- matched_pairs_report.txt — สรุปวิธีและผลเป็นข้อความ
- matched_pairs_growth_difference.svg — กราฟผลต่างรายประเทศ
- matched_pairs_period_comparison.csv — เปรียบเทียบช่วงหลัก 2000–2021 กับช่วงข้อมูลร่วมที่ยาวที่สุด
- matched_pairs_period_country_results.csv — ผลรายประเทศสำหรับสองช่วงวิเคราะห์
- matched_pairs_period_sensitivity_report.txt — รายงานจำนวนข้อมูล สถิติทดสอบ และข้อจำกัดของการตรวจช่วงยาว

ตัวอย่างรายงานและไฟล์จาก regression เดิมยังเก็บไว้ใน results/ เพื่อบันทึกการวิเคราะห์ระยะสำรวจ ไม่นับเป็นผลหลักฉบับปัจจุบัน
