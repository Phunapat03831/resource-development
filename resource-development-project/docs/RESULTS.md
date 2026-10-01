# ผลวิเคราะห์ที่มีในปัจจุบัน

ข้อมูลทั้งหมดด้านล่างเป็นผลเบื้องต้นจากปี 2000–2021 การตีความเป็นความสัมพันธ์ทางสถิติ ไม่ใช่เหตุและผล

## Regression หลายผลลัพธ์

แบบจำลองเดิมใส่ country fixed effects และ year fixed effects พร้อม standard errors จัดกลุ่มตามประเทศ โดยแต่ละ outcome ใช้ complete cases ของตัวเอง

| ผลลัพธ์ | สัมประสิทธิ์ total resource rents (% GDP) | p-value | 95% CI | Country-years | ประเทศ |
|---|---:|---:|---:|---:|---:|
| GDP growth | 0.138 | 0.014 | [0.027, 0.249] | 4,460 | 212 |
| GDP per capita growth | 0.117 | 0.039 | [0.006, 0.228] | 4,460 | 212 |
| Poverty gap | -0.029 | 0.575 | [-0.130, 0.072] | 1,695 | 165 |
| Gini index | 0.025 | 0.586 | [-0.065, 0.114] | 1,695 | 165 |
| Political stability score | 0.059 | 0.438 | [-0.090, 0.208] | 4,135 | 205 |

GDP growth และ GDP per capita growth มีสัมประสิทธิ์บวกใน baseline ส่วน poverty gap, Gini และ political stability ยังไม่พบความสัมพันธ์ชัดเจนทางสถิติใน specifications เหล่านี้ ความไม่ชัดเจนไม่ใช่หลักฐานว่าไม่มีความสัมพันธ์ โดยเฉพาะเมื่อข้อมูล poverty/Gini มีจำนวนแถวน้อยกว่า

## GDP ต่อหัวเติบโต: ตัวแปรควบคุม

ผลใน `growth_control_regression_coefficients.csv` ใช้ country/year dummies และ country-clustered sandwich standard errors พร้อม finite-sample correction; p-values ใช้การประมาณแบบ normal และช่วง 95% ใช้ coefficient ± 1.96 standard errors.

| แบบจำลอง | Coefficient: resource rents | SE (clustered) | p-value | 95% CI | N | ประเทศ |
|---|---:|---:|---:|---:|---:|---:|
| Baseline บน core sample | 0.147 | 0.046 | 0.0014 | [0.057, 0.238] | 4,251 | 210 |
| Core: log GDP ต่อหัวปีก่อน + population growth | 0.158 | 0.058 | 0.0061 | [0.045, 0.270] | 4,251 | 210 |
| Baseline บน expanded sample | 0.176 | 0.049 | 0.0003 | [0.080, 0.273] | 3,503 | 183 |
| Core controls บน expanded sample | 0.210 | 0.062 | 0.0007 | [0.088, 0.331] | 3,503 | 183 |
| เพิ่ม gross capital formation + trade | 0.197 | 0.057 | 0.0006 | [0.085, 0.309] | 3,503 | 183 |

แบบจำลอง core เทียบ baseline บน sample เดียวกันแล้ว สัมประสิทธิ์ resource rents ยังเป็นบวก การเพิ่ม investment และ trade ไม่ทำให้สัญญาณนี้หายไป แต่ sample ลดจาก 4,251 เป็น 3,503 country-years เมื่อเทียบแบบจำลอง expanded กับ core จึงไม่ควรอธิบายความต่างของขนาดสัมประสิทธิ์ว่าเกิดจาก controls อย่างเดียว

## Robustness: resource rents ปีก่อน

เมื่อเปรียบเทียบ current-year กับ previous-year rents ใน sample เดียวกันและควบคุม log GDP ต่อหัวปีก่อนกับ population growth:

- Same-year rents: coefficient 0.163, p=0.0049, N=4,243, 210 ประเทศ
- Previous-year rents: coefficient 0.066, p=0.246, N=4,243, 210 ประเทศ

ความสัมพันธ์บวกของปีปัจจุบันยังเห็นใน sample นี้ แต่ไม่พบหลักฐานชัดว่าค่า rents ของปีก่อนสัมพันธ์กับการเติบโตในปีถัดมา ควรอธิบายเป็น robustness check ไม่ใช่หลักฐาน causal timing

## หน่วยและการอ่านสัมประสิทธิ์

Resource rents มีหน่วยเป็น % of GDP. การเพิ่มขึ้น 1 หน่วยหมายถึงเพิ่ม 1 จุดเปอร์เซ็นต์ของ GDP ไม่ใช่เพิ่มขึ้น 1%. ผลลัพธ์ GDP per capita growth ก็วัดเป็นเปอร์เซ็นต์ จึงอ่าน coefficient 0.158 เป็นความสัมพันธ์กับการเติบโตที่สูงขึ้นประมาณ 0.158 จุดเปอร์เซ็นต์ เมื่อ resource rents สูงขึ้น 1 จุดเปอร์เซ็นต์ของ GDP โดยกำหนดตัวแปรอื่นและ fixed effects คงที่

## ไฟล์ผลลัพธ์

- `data/processed/results/resource_curse_regression_coefficients.csv`
- `data/processed/results/resource_curse_regression_summaries.txt`
- `data/processed/results/growth_lag_robustness.csv`
- `data/processed/results/growth_lag_robustness.txt`
- `data/processed/results/growth_control_regression_coefficients.csv`
- `data/processed/results/growth_control_regression_summary.txt`
- `data/processed/results/descriptive_statistics.csv`
