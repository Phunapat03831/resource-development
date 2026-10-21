# ผลวิเคราะห์ที่มีในปัจจุบัน

วิธีหลักที่ปรับตามคำแนะนำอาจารย์คือ matched-pairs t-test ด้านล่าง ส่วน regression ที่ตามมาเป็นผลจากระยะสำรวจก่อนเปลี่ยนวิธี ไม่ใช่ผลหลักของฉบับปัจจุบัน ทุกผลใช้ข้อมูล WDI ช่วงปี 2000–2021 และไม่ควรตีความเป็นเหตุและผล

## ผลหลักปัจจุบัน: matched pairs

ใช้ประเทศ/เขตเศรษฐกิจเป็นคู่ของตัวเอง เปรียบเทียบค่าเฉลี่ย GDP per capita growth ในปีที่ resource rents ต่ำกับปีที่ resource rents สูงของหน่วยเดียวกัน จัดกลุ่มโดยใช้เปอร์เซ็นไทล์ 33 และ 67 ภายในแต่ละหน่วย แล้วตัดช่วงกลางออก กำหนดให้มีอย่างน้อย 3 ปีที่มีข้อมูลครบในแต่ละกลุ่ม และไม่ใช้หน่วยที่จุดตัดของกลุ่มต่ำ/สูงแยกกันไม่ได้ จาก 217 หน่วยใน panel มี 5 หน่วยที่ไม่มีปีใดมีทั้งสองตัวแปร, 22 หน่วยมีจุดตัดไม่ต่างกัน, 1 หน่วยมีปีข้อมูลไม่พอ จึงวิเคราะห์ได้ 189 คู่

| สถิติ | ผล |
|---|---:|
| Country-years ที่มีทั้ง rents และ growth | 4,460 |
| คู่ประเทศ/เขตเศรษฐกิจที่ผ่านเกณฑ์ | 189 |
| ค่าเฉลี่ยการเติบโตระดับประเทศ ช่วง rents ต่ำ | 1.416% |
| ค่าเฉลี่ยการเติบโตระดับประเทศ ช่วง rents สูง | 2.642% |
| ผลต่างเฉลี่ยรายคู่ (สูง − ต่ำ) | 1.226 จุดเปอร์เซ็นต์ |
| SD ของผลต่างรายคู่ | 3.854 จุดเปอร์เซ็นต์ |
| 95% CI ของผลต่างเฉลี่ย | [0.673, 1.779] |
| Paired t-test, t(188) | 4.373 |
| p-value แบบสองด้าน | 0.000020 |
| Wilcoxon signed-rank sensitivity p-value | 0.000011 |
| Cohen's dz | 0.318 |

เมื่อใช้เกณฑ์นัยสำคัญ 5% ให้ปฏิเสธ H0 ที่ว่าผลต่างเฉลี่ยเป็นศูนย์ เพราะ p-value ต่ำกว่า 0.05 และช่วงความเชื่อมั่นไม่คร่อมศูนย์ ในเชิงขนาด ค่าเฉลี่ยรายประเทศในกลุ่มปี rents สูงมากกว่ากลุ่มต่ำประมาณ 1.23 จุดเปอร์เซ็นต์; 121 คู่มีผลต่างบวกและ 68 คู่มีผลต่างลบ

ผลนี้เปรียบเทียบค่าเฉลี่ยหลายปีของแต่ละกลุ่มภายในประเทศเดียวกัน ไม่ได้แปลว่า resource rents เพิ่ม 1 จุดเปอร์เซ็นต์แล้วการเติบโตจะเพิ่ม 1.23 จุดเปอร์เซ็นต์ และไม่ได้พิสูจน์ว่า rents เป็นสาเหตุ การทดสอบไม่ได้ควบคุมความเปลี่ยนแปลงร่วมตามปีหรือปัจจัยอื่นที่เปลี่ยนตามเวลา แต่ประเทศ/เขตเศรษฐกิจแต่ละแห่งได้รับน้ำหนักเท่ากัน

ไฟล์ที่สร้าง:

- `data/processed/results/matched_pairs_summary.csv` — ผลรวมของการทดสอบ
- `data/processed/results/matched_pairs_country_results.csv` — ค่าเฉลี่ยและผลต่างของแต่ละคู่
- `data/processed/results/matched_pairs_country_year_groups.csv` — ปีและกลุ่ม rents ต่ำ/กลาง/สูงของหน่วยที่ผ่านเกณฑ์
- `data/processed/results/matched_pairs_report.txt` — คำอธิบายวิธีและผลแบบข้อความ
- `data/processed/results/matched_pairs_growth_difference.svg` — กราฟแสดงผลต่างรายคู่

## ผลจาก regression ระยะสำรวจ (ไม่ใช่ผลหลักปัจจุบัน)

### Regression หลายผลลัพธ์

แบบจำลองเดิมใส่ country fixed effects และ year fixed effects พร้อม standard errors จัดกลุ่มตามประเทศ โดยแต่ละ outcome ใช้ complete cases ของตัวเอง

| ผลลัพธ์ | สัมประสิทธิ์ total resource rents (% GDP) | p-value | 95% CI | Country-years | ประเทศ |
|---|---:|---:|---:|---:|---:|
| GDP growth | 0.138 | 0.014 | [0.027, 0.249] | 4,460 | 212 |
| GDP per capita growth | 0.117 | 0.039 | [0.006, 0.228] | 4,460 | 212 |
| Poverty gap | -0.029 | 0.575 | [-0.130, 0.072] | 1,695 | 165 |
| Gini index | 0.025 | 0.586 | [-0.065, 0.114] | 1,695 | 165 |
| Political stability score | 0.059 | 0.438 | [-0.090, 0.208] | 4,135 | 205 |

GDP growth และ GDP per capita growth มีสัมประสิทธิ์บวกใน baseline ส่วน poverty gap, Gini และ political stability ยังไม่พบความสัมพันธ์ชัดเจนทางสถิติใน specifications เหล่านี้ ความไม่ชัดเจนไม่ใช่หลักฐานว่าไม่มีความสัมพันธ์ โดยเฉพาะเมื่อข้อมูล poverty/Gini มีจำนวนแถวน้อยกว่า

### GDP ต่อหัวเติบโต: ตัวแปรควบคุม

ผลใน `growth_control_regression_coefficients.csv` ใช้ country/year dummies และ country-clustered sandwich standard errors พร้อม finite-sample correction; p-values ใช้การประมาณแบบ normal และช่วง 95% ใช้ coefficient ± 1.96 standard errors.

| แบบจำลอง | Coefficient: resource rents | SE (clustered) | p-value | 95% CI | N | ประเทศ |
|---|---:|---:|---:|---:|---:|---:|
| Baseline บน core sample | 0.147 | 0.046 | 0.0014 | [0.057, 0.238] | 4,251 | 210 |
| Core: log GDP ต่อหัวปีก่อน + population growth | 0.158 | 0.058 | 0.0061 | [0.045, 0.270] | 4,251 | 210 |
| Baseline บน expanded sample | 0.176 | 0.049 | 0.0003 | [0.080, 0.273] | 3,503 | 183 |
| Core controls บน expanded sample | 0.210 | 0.062 | 0.0007 | [0.088, 0.331] | 3,503 | 183 |
| เพิ่ม gross capital formation + trade | 0.197 | 0.057 | 0.0006 | [0.085, 0.309] | 3,503 | 183 |

แบบจำลอง core เทียบ baseline บน sample เดียวกันแล้ว สัมประสิทธิ์ resource rents ยังเป็นบวก การเพิ่ม investment และ trade ไม่ทำให้สัญญาณนี้หายไป แต่ sample ลดจาก 4,251 เป็น 3,503 country-years เมื่อเทียบแบบจำลอง expanded กับ core จึงไม่ควรอธิบายความต่างของขนาดสัมประสิทธิ์ว่าเกิดจาก controls อย่างเดียว

### Robustness: resource rents ปีก่อน

เมื่อเปรียบเทียบ current-year กับ previous-year rents ใน sample เดียวกันและควบคุม log GDP ต่อหัวปีก่อนกับ population growth:

- Same-year rents: coefficient 0.163, p=0.0049, N=4,243, 210 ประเทศ
- Previous-year rents: coefficient 0.066, p=0.246, N=4,243, 210 ประเทศ

ความสัมพันธ์บวกของปีปัจจุบันยังเห็นใน sample นี้ แต่ไม่พบหลักฐานชัดว่าค่า rents ของปีก่อนสัมพันธ์กับการเติบโตในปีถัดมา ควรอธิบายเป็น robustness check ไม่ใช่หลักฐาน causal timing

### หน่วยและการอ่านสัมประสิทธิ์

Resource rents มีหน่วยเป็น % of GDP. การเพิ่มขึ้น 1 หน่วยหมายถึงเพิ่ม 1 จุดเปอร์เซ็นต์ของ GDP ไม่ใช่เพิ่มขึ้น 1%. ผลลัพธ์ GDP per capita growth ก็วัดเป็นเปอร์เซ็นต์ จึงอ่าน coefficient 0.158 เป็นความสัมพันธ์กับการเติบโตที่สูงขึ้นประมาณ 0.158 จุดเปอร์เซ็นต์ เมื่อ resource rents สูงขึ้น 1 จุดเปอร์เซ็นต์ของ GDP โดยกำหนดตัวแปรอื่นและ fixed effects คงที่

## ไฟล์ผลลัพธ์

- `data/processed/results/resource_curse_regression_coefficients.csv`
- `data/processed/results/resource_curse_regression_summaries.txt`
- `data/processed/results/growth_lag_robustness.csv`
- `data/processed/results/growth_lag_robustness.txt`
- `data/processed/results/growth_control_regression_coefficients.csv`
- `data/processed/results/growth_control_regression_summary.txt`
- `data/processed/results/descriptive_statistics.csv`
