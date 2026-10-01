# Data dictionary

## หน่วยสังเกตและช่วงเวลา

หนึ่งแถวหมายถึงหนึ่งประเทศหรือเขตเศรษฐกิจในหนึ่งปี ชุดข้อมูลตั้งต้นครอบคลุมปี 2000–2021 หลังตัดกลุ่มรวมเหลือ 4,774 country-years และ 217 หน่วย ไม่มี country-year ซ้ำในการตรวจล่าสุด จำนวนข้อมูลจริงของแต่ละตัวแปรไม่เท่ากันเพราะ missing values

## ตัวแปรจาก `data.xlsx`

| ชื่อตัวแปรในชุดข้อมูล | WDI Series Code | หน่วย/ความหมาย |
|---|---|---|
| `total_resource_rents_pct_gdp` | `NY.GDP.TOTL.RT.ZS` | ค่าเช่าทรัพยากรธรรมชาติรวม เป็น % ของ GDP; ตัวแทนการพึ่งพาทรัพยากร |
| `natural_gas_rents_pct_gdp` | `NY.GDP.NGAS.RT.ZS` | ค่าเช่าก๊าซธรรมชาติ เป็น % ของ GDP |
| `oil_rents_pct_gdp` | `NY.GDP.PETR.RT.ZS` | ค่าเช่าน้ำมัน เป็น % ของ GDP |
| `coal_rents_pct_gdp` | `NY.GDP.COAL.RT.ZS` | ค่าเช่าถ่านหิน เป็น % ของ GDP |
| `mineral_rents_pct_gdp` | `NY.GDP.MINR.RT.ZS` | ค่าเช่าแร่ เป็น % ของ GDP |
| `forest_rents_pct_gdp` | `NY.GDP.FRST.RT.ZS` | ค่าเช่าป่าไม้ เป็น % ของ GDP |
| `gdp_growth_pct` | `NY.GDP.MKTP.KD.ZG` | การเติบโตของ GDP รายปี (%) |
| `gdp_per_capita_growth_pct` | `NY.GDP.PCAP.KD.ZG` | การเติบโตของ GDP ต่อหัวรายปี (%) |
| `poverty_gap_3usd_pct` | `SI.POV.GAPS` | ช่องว่างความยากจนที่เส้น $3.00 ต่อวัน (2021 PPP), % |
| `gini_index` | `SI.POV.GINI` | ดัชนี Gini ตามนิยาม WDI; สเกลในไฟล์ 0–100 |
| `political_stability_score_0_100` | `GOV_WGI_PV_SC` | Political Stability governance score; สเกล 0–100 คะแนนสูงหมายถึงเสถียรภาพสูงกว่า |

## ตัวแปรจาก `adddata.xlsx`

| ชื่อตัวแปรในชุดข้อมูล | WDI Series Code | หน่วย/การใช้ |
|---|---|---|
| `gdp_per_capita_constant_2015_usd` | `NY.GDP.PCAP.KD` | GDP ต่อหัว ดอลลาร์สหรัฐราคาคงที่ปี 2015; ใช้คำนวณค่าลอการิทึมของปีก่อนหน้า |
| `population_growth_pct` | `SP.POP.GROW` | การเติบโตของประชากรรายปี (%) |
| `gross_capital_formation_pct_gdp` | `NE.GDI.TOTL.ZS` | Gross capital formation (% GDP); ใช้ในแบบจำลองเสริม |
| `trade_pct_gdp` | `NE.TRD.GNFS.ZS` | การค้าสินค้าและบริการ (% GDP); ใช้ในแบบจำลองเสริม |

ตัวแปรที่คำนวณเพิ่มสำหรับแบบจำลอง:

| ชื่อตัวแปร | นิยาม |
|---|---|
| `gdp_per_capita_previous_year` | GDP ต่อหัวจากปีปฏิทินก่อนหน้าของประเทศเดียวกัน |
| `log_gdp_per_capita_previous_year` | ลอการิทึมธรรมชาติของ GDP ต่อหัวปีก่อน ใช้เมื่อค่ามากกว่าศูนย์ |
| `resource_rents_pct_gdp_previous_year` | resource rents จากปีปฏิทินก่อนหน้า ไม่ถือว่าค่าห่างหลายปีเป็น lag 1 |

## ความครอบคลุมข้อมูล

| ตัวแปรใหม่ | Country-years ที่ไม่ missing | หน่วยที่มีข้อมูล |
|---|---:|---:|
| GDP per capita (2015 US$) | 4,549 | 213 |
| Population growth | 4,774 | 217 |
| Gross capital formation | 3,755 | 185 |
| Trade | 3,919 | 193 |

| ตัวแปรเดิม | Country-years ที่ไม่ missing | หน่วยที่มีข้อมูล |
|---|---:|---:|
| Total resource rents | 4,535 | 214 |
| GDP per capita growth | 4,555 | 214 |
| Poverty gap | 1,703 | 166 |
| Gini index | 1,703 | 166 |
| Political stability score | 4,240 | 206 |

## รหัสกลุ่มที่ถูกตัดออก

สคริปต์ตัดรหัส World Bank ที่แทนภูมิภาค กลุ่มรายได้ กลุ่มการเงิน หรือยอดรวมโลก เช่น `WLD`, `HIC`, `EAS`, `SSA`, `IBT` และรหัสกลุ่มที่พบในไฟล์ เช่น `INX` และ `PST` ออกรายการที่คัดพบได้ใน `data/processed/aggregate_rows_removed.csv`.

## แหล่งข้อมูลและใบอนุญาต

World Bank, [World Development Indicators](https://databank.worldbank.org/source/world-development-indicators). World Bank Data Catalog ระบุใบอนุญาต CC BY 4.0 สำหรับ WDI. ตัวแปรทรัพยากรธรรมชาติใช้ WDI series `NY.GDP.TOTL.RT.ZS` ซึ่ง metadata เชื่อมโยงกับ *The Changing Wealth of Nations*.
