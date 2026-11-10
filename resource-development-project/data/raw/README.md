# Raw source files

These workbooks are the World Bank World Development Indicators (WDI) snapshots used by this project. Keep the originals unchanged so processed outputs can be regenerated and compared with the source.

| File | Contents |
|---|---|
| `data.xlsx` | Resource-rent categories, growth outcomes, poverty, Gini, and political stability |
| `adddata.xlsx` | GDP per capita at constant 2015 US$, population growth, gross capital formation, and trade |
| `wdi_growth_rents_1960_2025.csv` | Two selected series: total natural resources rents and GDP per capita growth; download columns span 1960–2025, with joint observations available in 1970–2021. Used only for a longer-period sensitivity check. |

The original workbooks cover 2000–2021. The added CSV has year columns for 1960–2025, but both selected indicators overlap only in 1970–2021. WDI is available through [World Bank DataBank](https://databank.worldbank.org/source/world-development-indicators) and the [World Bank Data Catalog](https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators). The Data Catalog lists CC BY 4.0. Please retain attribution to the World Bank and note that this project reshapes, filters, merges, and analyzes the downloaded data.
