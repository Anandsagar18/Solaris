# SOLARIS

**Solar On-vehicle Long-horizon Assessment of Range, Insolation & Sufficiency**

A first-principles, drive-cycle- and climate-resolved methodology and open toolkit for
assessing **solar-assisted heavy electric vehicles**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-%E2%89%A53.9-blue)
![Deterministic](https://img.shields.io/badge/results-deterministic-success)

Companion code and data for:

> A. Gaikwad, A. Kumar, and A. Deo, "SOLARIS: A First-Principles, Drive-Cycle- and
> Climate-Resolved Methodology and Open Toolkit for Assessing Solar-Assisted Heavy
> Electric Vehicles," *IEEE International Transportation Electrification Conference
> and Expo, Asia-Pacific (ITEC-AP)*, 2026.

---

## What it does

SOLARIS answers one question honestly: *how close does a solar-skinned EV get to running
on sunlight alone, in a given climate and for a given daily use, and what would it take
to get all the way there?* It chains:

1. **Mass audit**: every harvesting subsystem is charged to the vehicle (182 kg → 2482 kg).
2. **Device-physics harvest models**: PV with temperature derating, a 1-D thermal-resistance
   model of a skin-mounted TEG (shows it is gradient-starved, ≈0.019 kWh/day), regenerative
   braking and regenerative suspension.
3. **WLTP Class 3b propulsion**: a statistics-matched 1 Hz reconstruction (+0.11 % distance).
4. **8760-hour SoC simulation** with commute schedule, parked cabin-conditioning load,
   grid top-ups and a periodic (warm-started) year, so initial charge is not counted as solar.
5. **Five-tier sufficiency metric** `f_ss = E_harv / E_dem`
   (self-sufficient ≥ 1 · quasi ≥ 0.9 · highly ≥ 0.8 · moderately ≥ 0.5 · grid-dependent).
6. **Closed-form design inversion**: required PV area for a range, or max range for an area.
7. **Economics, grid relief and a multi-objective (grid / mass / cost) sweep.**
8. **Two-tier check against satellite-derived resource data**: Global Solar Atlas annual
   resource (Tier 1) and hourly TMY series from NSRDB / PVGIS (Tier 2) for **all three study
   cities**. These are satellite-based model products, not ground measurements.

## Headline results (seven-seat demonstrator, 11.6 m² PV skin)

| Scenario | City | f_ss idealized | f_ss satellite annual (T1) | **f_ss satellite hourly TMY (T2)** | Plug-ins/yr on T2 (no solar) | Relief on T2 |
|---|---|---|---|---|---|---|
| II · 50 km/day urban | Phoenix | 0.94 | 0.88 | **0.83** (highly solar-assisted) | 5 (27) | 82 % |
| II · 50 km/day urban | Lucknow | 0.77 | 0.72 | **0.71** (moderately solar-assisted) | 8 (27) | 71 % |
| II · 50 km/day urban | London  | 0.51 | 0.53 | **0.52** (moderately solar-assisted) | 12 (24) | 52 % |
| I · 100 km/day mixed | Phoenix | 0.47 | 0.44 | **0.42** (grid-dependent) | 31 (54) | 42 % |
| I · 100 km/day mixed | Lucknow | 0.39 | 0.36 | **0.36** (grid-dependent) | 35 (53) | 36 % |
| I · 100 km/day mixed | London  | 0.24 | 0.25 | **0.25** (grid-dependent) | 39 (50) | 25 % |

* Not self-sufficient in any city on the TMY; up to **82 % of yearly demand from on-board
  harvest** and **81 % fewer plug-ins** (Phoenix, light use).
* Self-sufficiency at 50 km/day (TMY) needs **14.4 m²** of PV in Phoenix, 16.9 m² in Lucknow
  and **23.9 m²** in London.
* The real weather series lower the Phoenix score by **0.11** relative to the idealized
  synthetic climate (0.058 from the yearly total, 0.047 from cloud timing).
* Phoenix results are stable across NSRDB TMY-2022/2023/2024/2025 (f_ss 0.832–0.840).
* A larger battery lowers f_ss slightly through its mass; it is sized for range, not solar capture.

## Repository layout

```
Solaris/
├── solaris.py              # the toolkit (single module, numpy only); `python solaris.py` prints every number
├── make_figures.py         # regenerates every figure into figures/ (needs matplotlib)
├── requirements.txt
├── data/                   # satellite-derived climate data, grouped by city (see data/README.md)
│   ├── phoenix/
│   │   ├── global_solar_atlas/   GSA_Report_Phoenix.{pdf,xlsx}
│   │   └── nsrdb_tmy/            323705_33.45_-112.06_tmy-{2022,2023,2024,2025}.csv
│   ├── lucknow/
│   │   ├── global_solar_atlas/   GSA_Report_Lucknow.{pdf,xlsx}
│   │   └── nsrdb_tmy/            46088_26.85_80.95_tmy.csv
│   └── london/
│       ├── global_solar_atlas/   GSA_Report_London.{pdf,xlsx}
│       ├── pvgis_tmy/            tmy_51.526_-0.129_2005_2023.csv
│       └── pvgis_supplementary/  PVGIS tilted-plane time series + 1 kWp PV report
├── docs/
│   ├── METHODOLOGY.md      # equations, parameters, assumptions
│   ├── REPRODUCING.md      # paper table/figure  →  function that emits it
│   └── API.md              # public functions and how to retarget the toolkit
├── figures/                # generated PNG (300 dpi) + PDF
├── results/
│   └── reference_output.txt  # full console output of `python solaris.py`
├── tests/
│   └── test_reproduce.py   # regression tests for every headline number
├── CITATION.cff
├── CHANGELOG.md
└── LICENSE
```

## Quick start

```bash
git clone https://github.com/Anandsagar18/Solaris.git
cd Solaris
python -m pip install -r requirements.txt

python solaris.py          # all tables / numbers (~1 s)
python make_figures.py     # all figures -> figures/ (~6 s)
python -m pytest -q        # regression tests (optional; pip install pytest)
```

Everything is deterministic (fixed random seeds), so your output should match
[`results/reference_output.txt`](results/reference_output.txt) exactly.

## Using the toolkit

```python
import solaris as s

# 1. Score the demonstrator on the idealized synthetic climate
r = s.simulate("Phoenix", daily_km=50, city=True)
print(round(r["fss"], 2), r["charges"], s.classify(r["fss"]))  # 0.94 6 quasi-self-sufficient

# 2. Same, on the satellite-derived hourly TMY shipped in data/ (the paper's main results)
tmy = s.load_city_tmy("Phoenix")
r = s.simulate("Phoenix", 50, True, climate=tmy)
print(round(r["fss"], 2), r["charges"], round(r["relief"], 2))  # 0.83 5 0.82

# 3. Design inversion (closed form); pass climate= to use the TMY
s.required_pv_area(50, True, "Phoenix", climate=tmy)      # 14.4 m^2
s.max_selfsuff_km("Phoenix", city=True, climate=tmy)      # 37.5 km/day

# 4. Checks against satellite-derived resource data
s.real_data_validation()      # Tier 1: Global Solar Atlas annual GHI + temperature
s.tmy_validation()            # Tier 2: hourly TMY, all three cities
s.gap_decomposition()         # idealized -> TMY gap split into magnitude / timing
s.tmy_robustness()            # Phoenix across NSRDB TMY releases
s.design_levers_tmy()         # kappa, eta_regen, suspension, area for f_ss = 1, pack sweep

# 5. Economics and multi-objective sweep (mass fed back into consumption)
s.economics("Phoenix", 50, True, climate=tmy)
s.pareto("Phoenix", 50, True, climate=tmy)

# 6. Your own site: any NSRDB or PVGIS TMY CSV (auto-detected, converted to local time)
ghi, T = s.load_tmy("my_site_tmy.csv", utc_offset=+1)   # utc_offset needed for PVGIS only
s.simulate("London", 50, True, climate=(ghi, T))
```

To study a different vehicle, edit the constants block (`Cd`, `Af`, `Cr`, `A_skin`,
`eta_pv`, …), the `MASS` audit dictionary, or the `WLTC` phase table. To add a city, add
an entry to `LOCS` (latitude, assumed PSH, mean temperature, seasonal amplitude) and,
optionally, to `GSA`, `TMY_FILES` and `UTC_OFFSET`. See [docs/API.md](docs/API.md).

## Data

All climate inputs are included and grouped by city; provenance, coordinates, retrieval
settings and licences are in [data/README.md](data/README.md).

| City | Annual resource (Tier 1) | Hourly TMY (Tier 2) | TMY annual GHI vs GSA |
|---|---|---|---|
| Phoenix, USA | Global Solar Atlas, 2119.4 kWh/m²/yr | NREL NSRDB PSM v4.0.1, TMY-2023 (+2022, 2024, 2025) | 2110.0 (−0.4 %) |
| Lucknow, India | Global Solar Atlas, 1725.6 kWh/m²/yr | NREL NSRDB SUNY International TMY | 1843.6 (+6.8 %) |
| London, UK | Global Solar Atlas, 1032.7 kWh/m²/yr | EC-JRC PVGIS 5.3 (SARAH-3, 2005–2023) TMY | 1050.7 (+1.7 %) |

NSRDB and PVGIS files store UTC timestamps; `load_tmy()` converts them to local standard
time (Phoenix UTC−7, Lucknow UTC+5:30, London UTC+0) so the commute schedule lines up
with local daylight.

## Reproducing the paper

Every table and figure in the paper maps to one function; see
[docs/REPRODUCING.md](docs/REPRODUCING.md). The paper's LaTeX source is in [`paper/`](paper/).

## Citation

If you use SOLARIS, please cite the paper (and, optionally, the software, see
[CITATION.cff](CITATION.cff)):

```bibtex
@inproceedings{gaikwad2026solaris,
  author    = {Gaikwad, Anandsagar and Kumar, Aditya and Deo, Arjun},
  title     = {{SOLARIS}: A First-Principles, Drive-Cycle- and Climate-Resolved Methodology
               and Open Toolkit for Assessing Solar-Assisted Heavy Electric Vehicles},
  booktitle = {Proc. IEEE International Transportation Electrification Conference and Expo,
               Asia-Pacific (ITEC-AP)},
  year      = {2026}
}
```

## Use of generative AI

Following IEEE policy, the authors disclose that Claude (Anthropic) and ChatGPT (OpenAI)
were used for: (i) paraphrasing and language editing of the manuscript text; (ii) formatting
the LaTeX source to the IEEE conference template; (iii) assistance in writing, refactoring
and debugging the Python toolkit and figure scripts, and in drafting this documentation; The
methodology, modeling assumptions, analyses and conclusions are the authors' own. All
AI-assisted text and code were reviewed and edited by the authors, and every reported number
is reproduced by running this repository.

## Limitations

The results are analytical projections, not measurements of a built vehicle: a
statistics-matched (not certified) WLTP trace, single-point cost and tariff estimates on
different bases (average vs marginal rates), satellite-derived (not ground-measured) climate
data, one
representative year without degradation, a lumped cabin-conditioning model, and no
route-level shading. See Section V of the paper and [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Authors

* **Anandsagar Gaikwad**, Dept. of CSE, Rajiv Gandhi Institute of Petroleum Technology (RGIPT), Jais, India
* **Aditya Kumar**, Dept. of CSE, RGIPT, Jais, India
* **Arjun Deo**, RGIPT Bengaluru Campus, India

## License

Code: [MIT](LICENSE). Third-party data in `data/` keep their own licences (Global Solar
Atlas: CC BY 4.0; NSRDB: public NREL data; PVGIS: © European Union, reuse authorised with
acknowledgement). See [data/README.md](data/README.md).