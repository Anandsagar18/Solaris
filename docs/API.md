# SOLARIS API reference

`solaris.py` is a single module with no dependencies beyond numpy. All functions are
pure except where they temporarily modify a module-level constant and restore it
(`validate()`, `regen_susp_sensitivity()`, `real_data_validation()`, `gap_decomposition()`).

## Core simulation

| Function | Returns |
|---|---|
| `simulate(loc, daily_km, city, variant="P0", kappa=0.80, eta_regen=0.60, floor=0.10, recharge_to=0.80, seed=0, pv_scale=1.0, A_over=None, cap_over=None, climate=None, m_over=None, warmup=True)` | dict: `fss`, `relief`, `grid_kwh`, `charges`, `curtailed`, `ann_dem`, `ann_harv`, `solar_used`, `soc_change`, `psh`, `whkm`, `cap`, `soc` (8761-point % trace) |
| `classify(fss)` | tier name |
| `whkm(variant, city=False, eta_regen=0.60)` | Wh/km on the reconstructed WLTP 3b (city = Low + Medium) |
| `wltp_trace(keys)` / `build_phase(D_km, T_s, vmax_kmh, n)` | 1 Hz speed trace (m/s) |
| `consumption_wh_km(v_ms, m, eta_regen)` | (Wh/km, distance km, mean speed km/h) |

`loc` is a key of `LOCS` (`"Phoenix"`, `"Lucknow"`, `"London"`). `city=True` uses the
urban phases (Scenario II); `False` the full cycle (Scenario I). Pass
`climate=(ghi_W_m2, temp_C)` (two 8760 arrays) to override the synthetic climate.

## Climate data

| Function | Purpose |
|---|---|
| `hourly_climate(lat, psh_target, Tmean, Tamp, seed=0)` | synthetic 8760-h GHI and temperature |
| `load_tmy(path, utc_offset=None)` | read NSRDB or PVGIS TMY CSV, converted to local standard time |
| `load_city_tmy(city)` | shipped TMY for a study city, or `None` |
| `climate_error(loc)` | monthly synthetic vs satellite-TMY GHI and MAPE |

## Validation and analysis

| Function | Purpose |
|---|---|
| `validate()` | Lightyear 0 / Aptera cross-validation |
| `real_data_validation()` | Tier 1: Global Solar Atlas annual GHI and temperature |
| `tmy_validation()` | Tier 2: satellite-derived hourly TMY, all cities |
| `gap_decomposition(km=50, city=True)` | magnitude (TMY's own annual GHI + mean T) vs timing split of the synthetic → TMY gap |
| `tmy_robustness()` | Phoenix across NSRDB TMY releases |
| `required_pv_area(daily_km, city, loc, climate=None)` / `max_selfsuff_km(loc, city, climate=None, A=None)` | closed-form design inversion (battery-side c); pass `climate=load_city_tmy(loc)` for the TMY |
| `engine_fT(loc, climate=None)` / `engine_Eaux(loc, city, daily_km, climate=None)` | climate-consistent inputs to the closed form |
| `economics(loc, km, city, cost=None, climate=None)` | relief, savings, payback (full and PV-only) |
| `pareto(loc, km, city, climate=None, areas=(8, 11.6, 15, 20), caps=(150, 200, 250, 300))` | PV area × pack sweep with mass feedback (grid, relief, mass, cost, f_ss) |
| `design_levers_tmy(loc, km, city)` | Sec. V-D sensitivities on the TMY |
| `teg_daily_kwh(...)`, `teg_tradeoff()`, `regen_susp_sensitivity()` | component studies |
| `wltp_recon_error()` | reconstruction error vs official WLTC 3b statistics |

## Retargeting

* **Vehicle**: edit `Cd`, `Af`, `Cr`, `eta_dt`, `A_skin`, `eta_pv`, `beta`, `MASS`, `CAP`.
* **Drive cycle**: edit `WLTC` (distance km, duration s, peak km/h, micro-trips), or pass
  your own trace to `consumption_wh_km()`.
* **New city**: add `LOCS["Name"] = (lat, assumed_PSH, T_mean, T_amplitude)`; optionally
  `GSA["Name"]`, `TMY_FILES["Name"]` and `UTC_OFFSET["Name"]`, then call
  `simulate("Name", …, climate=load_city_tmy("Name"))`.
* **Costs/tariffs**: edit `COST_ITEMS` and `PRICE`.
