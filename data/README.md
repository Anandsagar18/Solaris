# Climate data (grouped by city)

All resource data here are **satellite-derived model products** (Solargis for Global Solar
Atlas, NREL PSM/SUNY for NSRDB, SARAH-3 for PVGIS), calibrated against ground stations.
They are the standard substitute for long-term ground measurements, not measurements.

All files are original downloads, unmodified. `solaris.py` reads them through
`load_city_tmy()` / `load_tmy()`; the Global Solar Atlas numbers are transcribed into the
`GSA` dictionary in `solaris.py` (the `.xlsx` reports are the source of record).

```
data/
├── phoenix/
│   ├── global_solar_atlas/  GSA_Report_Phoenix.pdf, GSA_Report_Phoenix.xlsx
│   └── nsrdb_tmy/           323705_33.45_-112.06_tmy-2022.csv
│                            323705_33.45_-112.06_tmy-2023.csv   <- used for Tier 2
│                            323705_33.45_-112.06_tmy-2024.csv
│                            323705_33.45_-112.06_tmy-2025.csv
├── lucknow/
│   ├── global_solar_atlas/  GSA_Report_Lucknow.pdf, GSA_Report_Lucknow.xlsx
│   └── nsrdb_tmy/           46088_26.85_80.95_tmy.csv           <- used for Tier 2
└── london/
    ├── global_solar_atlas/  GSA_Report_London.pdf, GSA_Report_London.xlsx
    ├── pvgis_tmy/           tmy_51.526_-0.129_2005_2023.csv     <- used for Tier 2
    └── pvgis_supplementary/ Timeseries_51.526_-0.129_SA3_39deg_0deg_2005_2005.csv
                             PVGIS-5_GridConnectedPV_51.509_-0.135_CrystSi_1kWp_14_35deg_0deg.pdf
```

## Tier 1: Global Solar Atlas (annual resource)

Site reports generated on **18 Jul 2026** from <https://globalsolaratlas.info/>
(Solargis for the World Bank Group). Long-term averages:

| City | Coordinates | GHI (kWh/m²/yr) | DNI | GTI at opt. tilt | DIF | Air temp. (°C) | Elevation (m) | Time zone |
|---|---|---|---|---|---|---|---|---|
| Phoenix | 33.543171, −112.073593 | **2119.4** | 2719.8 | 2440.5 (32°) | 478.4 | 23.1 | 369 | UTC−7 (MST, no DST) |
| Lucknow | 26.857530, 80.912659 | **1725.6** | 1145.5 | 1851.5 (24°) | 925.9 | 24.9 | 127 | UTC+5:30 (IST) |
| London | 51.501993, −0.119476 | **1032.7** | 883.8 | 1209.5 (36°) | 575.9 | 10.9 | 9 | UTC+0 (GMT) / +1 (BST) |

**GHI is the right quantity for an essentially horizontal vehicle skin.** Using GTI at
the optimum tilt would overstate on-vehicle yield by 7–17 %, and DNI by more.

## Tier 2: satellite-derived hourly typical meteorological years (8760 h)

| City | Source | Location / settings | File format | Timestamps |
|---|---|---|---|---|
| Phoenix | NREL **NSRDB**, Physical Solar Model **v4.0.1**, TMY-2022/2023/2024/2025 | location ID 323705, 33.45, −112.06, elev. 334 m | NSRDB CSV (2 metadata rows + header) | UTC (`Time Zone`=0, `Local Time Zone`=−7) |
| Lucknow | NREL **NSRDB SUNY International** (10 km, 2000–2014), TMY | location ID 46088, 26.85, 80.95 | NSRDB CSV | UTC (`Time Zone`=0, `Local Time Zone`=5.5) |
| London | EC-JRC **PVGIS 5.3** TMY generator, radiation database PVGIS-SARAH3, period 2005–2023 | 51.526, −0.129, elev. 36 m | PVGIS CSV (`time(UTC)`, `T2m`, `G(h)`, …) | UTC |

`load_tmy()` auto-detects the format, reads GHI and air temperature, and **rolls the
series to local standard time** (Phoenix −7 h, Lucknow +6 h after rounding 5.5 h, London
0 h) so that the 08:00/18:00 commute and the parked cabin load line up with local
daylight. Annual GHI of the TMY files vs Global Solar Atlas: Phoenix 2110.0 (−0.4 %),
Lucknow 1843.6 (+6.8 %), London 1050.7 (+1.7 %) kWh/m²/yr.

### Supplementary (not used by the engine)

* `london/pvgis_supplementary/Timeseries_…_SA3_39deg_0deg_2005_2005.csv`: PVGIS hourly
  in-plane irradiance, 39° (optimum) tilt, south-facing, year 2005, PVGIS-SARAH3.
* `london/pvgis_supplementary/PVGIS-5_GridConnectedPV_…pdf`: PVGIS grid-connected PV
  report for 1 kWp crystalline-Si, 35° tilt, 14 % system loss at 51.509, −0.135
  (1018.9 kWh/kWp/yr; in-plane 1261.0 kWh/m²/yr), generated 18 Jul 2026.

## How to re-download

* **Global Solar Atlas**: open the map at the coordinates above → *Site data* → *Export* (PDF/XLSX report).
* **NSRDB**: <https://nsrdb.nrel.gov/> → NSRDB Viewer → select the point → *USA & Americas*
  TMY (Phoenix, select `tmy-2022` … `tmy-2025`) or *SUNY International* TMY (Lucknow) →
  attributes GHI, DNI, DHI, Temperature, … (timestamps in UTC).
* **PVGIS**: <https://re.jrc.ec.europa.eu/pvg_tools/en/> → *TMY* tab → lat 51.526, lon −0.129,
  period 2005–2023 → CSV.

## Licences and attribution

* Global Solar Atlas data: © The World Bank Group / Solargis, released under the Creative
  Commons Attribution 4.0 licence (CC BY 4.0). Air temperature derived from ERA5 (© ECMWF,
  post-processed by Solargis).
* NSRDB data: National Renewable Energy Laboratory, U.S. Department of Energy, publicly
  available. Please cite M. Sengupta et al., "The National Solar Radiation Data Base
  (NSRDB)," *Renew. Sustain. Energy Rev.*, vol. 89, pp. 51–60, 2018.
* PVGIS data: © European Union, 2001–2026. Reproduction is authorised provided the source
  is acknowledged.
