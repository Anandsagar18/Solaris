# Changelog

## 1.1.0 (2026-10) — review corrections (changes results)

* **Bug fix: drivetrain efficiency was applied twice.** `whkm()` is battery-side (traction
  / eta_dt, regen x eta_regen x eta_dt), but `simulate()` and the closed-form inversion divided
  by eta_dt again. Removing the double count raises every f_ss (e.g. Phoenix II on the TMY
  0.78 -> 0.83, idealized 0.88 -> 0.94).
* **Periodic year**: the simulation is run twice and the second pass (starting from the first
  pass's end-of-year SoC) is reported, so the initial 90 % charge no longer counts as solar.
* **Relief** is now harvest actually used (harvest - curtailment) / demand, so relief <= f_ss
  (previously demand - grid, which could exceed f_ss).
* **Mass feedback**: `simulate(m_over=...)`; `pareto()` feeds PV and pack mass into
  consumption, so a bigger pack lowers f_ss.
* **Design inversion and economics accept `climate=`** (TMY); paper values now on the TMY.
* **Tariffs unrounded** with sourced FX (RBI reference rate; GBP/USD 21 Oct 2026).
* **Gap decomposition** uses the TMY's own annual GHI and mean temperature for the magnitude
  step (was Global Solar Atlas, which mixed database differences into the timing share).
* New `design_levers_tmy()`; wording "measured" -> "satellite-derived" throughout.
* Consistency pass: `simulate()`, `required_pv_area()` and `max_selfsuff_km()` return plain
  Python numbers (so the paper's listing prints `(0.83, 5)` under numpy 2); `pareto()` prices PV
  on the same basis as `economics()` (≈264 USD/m², was 400) and sweeps 150–300 kWh by default;
  the multi-objective printout now runs on the Phoenix TMY, as in the paper.

## 1.0.1 (2026-10) — sourced tariffs

* Electricity tariffs in `PRICE` now follow cited sources: Phoenix 0.16 USD/kWh (EIA via
  Arizona Corporation Commission), Lucknow 0.07 (UPPCL LMV-1, Rs 6.50/kWh), London 0.35
  (Ofgem price cap, 26.32 p/kWh). Scenario II payback: Lucknow 27.2 → 34.9 yr (PV-only
  12.7 → 16.3), London 11.5 → 11.2 yr (PV-only 5.4 → 5.2); Phoenix unchanged. No f_ss,
  grid-energy or design-inversion result changes.

## 1.0.0 (2026-10) — ITEC-AP 2026 release

* Satellite-derived hourly TMY validation (Tier 2; labelled "measured" in this release) now covers **all three cities**: added the NSRDB
  SUNY International TMY for Lucknow (f_ss 0.67 in Scenario II).
* Added `tmy_robustness()` (Phoenix NSRDB TMY-2022…2025) and `gap_decomposition()`.
* `load_tmy()` converts NSRDB/PVGIS UTC timestamps to local standard time (effect on
  results: f_ss unchanged to two decimals; Phoenix Scenario II grid energy 1056 → 1058 kWh/yr).
* Data reorganised by city under `data/<city>/`; paths resolved relative to `solaris.py`.
* WLTC 3b reference statistics corrected to the official values (High phase 7.162 km, total
  23.266 km); the reconstructed trace itself is unchanged.
* Production-vehicle references made battery-referenced and sourced (Aptera 65 Wh/km from
  42 kWh / 400 mi; Lightyear 0 96 Wh/km from 60 kWh / 625 km).
* New `make_figures.py` regenerates every figure; regression tests in `tests/`.

## Pre-release (2026-07) — journal draft

* Global Solar Atlas (Tier 1) and NSRDB/PVGIS hourly TMY (Tier 2, Phoenix and London) validation.
