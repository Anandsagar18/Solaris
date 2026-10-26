# SOLARIS methodology

This page documents every model, parameter and assumption in `solaris.py`. Section
numbers in brackets refer to the ITEC-AP 2026 paper.

```
mass audit ─► m ─┐
                 ├─► WLTP road-load integration ─► c (Wh/km)
PV / TEG / regen ┘                                  │
climate (synthetic | satellite TMY) ─► 8760-h SoC loop ◄┘ ─► f_ss, charges, grid kWh
                                         │
                                         ├─► design inversion (A_req, D_max)
                                         └─► economics, multi-objective sweep
```

## 1. Platform and mass audit [III-A]

| Parameter | Symbol | Value |
|---|---|---|
| Drag coefficient | `Cd` | 0.28 |
| Frontal area | `Af` | 2.9 m² |
| Rolling resistance | `Cr` | 0.010 |
| Air density | `rho` | 1.204 kg/m³ |
| Drivetrain efficiency | `eta_dt` | 0.92 |
| Regenerative-braking efficiency | `ETA_REGEN_BASE` | 0.60 (0.72 optimistic) |
| PV skin area | `A_skin` | 11.6 m² |
| PV efficiency / temp. coeff. | `eta_pv`, `beta` | 0.22, −0.4 %/K |
| PV real-world derating | `KAPPA_PV_BASE` | 0.80 |
| Usable pack (P0) | `CAP["P0"]` | 250 kWh |

The `MASS` dictionary charges every harvesting and integration item to the vehicle:
glider 1800 kg + 182 kg harvesting/integration + 500 kg pack (250 kWh at 500 Wh/kg) =
**2482 kg** (P0). Variant PA uses 350 Wh/kg (714 kg pack, 2696 kg).

## 2. Thermoelectric generator (TEG) thermal network [III-C]

`teg_daily_kwh()` solves a 1-D series network for a 2 m² Bi₂Te₃ module array under the
skin: leg conductance `k_TE·fill/leg` = 1.2·0.5/0.004 = 150 W/m²K, plus contact
resistance → ≈130 W/m²K. With absorbed flux α·G = 0.9·700 = 630 W/m² and skin loss
h = 15 W/m²K, the through-flux is q_th ≈ 565 W/m² and ΔT_leg ≈ 3.8 K. Matched-load
output (Seebeck 0.051 V/K per module, 3 Ω, 625 modules/m²) is ≈3.8 W, i.e.
**0.019 kWh/day** over 5 sun-hours; an optimized high-resistance TEG at 1 % of q_th caps
near 11 W. `teg_tradeoff()`: the 35 kg TEG, reallocated to the pack, would store 17.5 kWh,
which the TEG needs ≈921 days to generate.

## 3. WLTP Class 3b propulsion [III-B]

`build_phase()` reconstructs each WLTC 3b phase (official distance, duration, peak speed;
DieselNet) as *n* identical trapezoidal micro-trips (a_acc = 1.0, a_dec = 1.2 m/s²),
choosing the cruise speed that fits the phase distance and duration. Reconstruction
error (`wltp_recon_error()`): phase distances −0.71 % … +0.55 %, total 23.292 vs 23.266 km
(+0.11 %), mean speed 46.5 km/h, peak 124.7 vs 131.3 km/h.

`consumption_wh_km()` integrates at 1 Hz:

    F = Cr·m·g·[v>0.1] + ½·rho·Cd·Af·v² + m·a,     P = F·v
    E_batt = E_pos/eta_dt + E_neg·eta_regen·eta_dt

Result (P0): **237 Wh/km** combined, **210 Wh/km** city (Low + Medium phases). These are
BATTERY-side values: η_dt and regeneration are already inside, so the simulation and the
closed form use them directly (v1.0.x divided by η_dt a second time; fixed in v1.1.0).

## 4. Climate [V-A, V-B]

* **Synthetic** (`hourly_climate()`): clear-sky GHI ∝ cos(z)^1.15 × seasonal clearness
  Kt = 0.75 + 0.10 cos(2π(d−172)/365), with a Gaussian monsoon dip (−0.20, centred on
  day 200, σ = 25 d) for latitudes < 30° (Lucknow), × a Gaussian daily multiplier
  (mean 1, σ = 0.18, seed 0; GHI clipped at 0), rescaled to the assumed annual PSH (6.3 / 5.2 / 2.7). Temperature is
  seasonal + diurnal sinusoids.
* **Satellite-derived TMY** (`load_tmy()`, `load_city_tmy()`): NSRDB or PVGIS hourly TMY,
  converted from UTC to local standard time (see `data/README.md`). These are satellite-based
  model products calibrated against ground stations, not ground measurements.

## 5. 8760-hour simulation [III-D]

`simulate()` steps hour by hour:

* **Driving**: two trips at 08:00 and 18:00 local time; propulsion energy is distance-based
  (`whkm × trip_km`), while suspension harvest and driving-mode auxiliary load are
  prorated by the actual trip duration `daily_km / v̄ / 2`.
* **PV**: `E_pv = A·eta_pv·(G/1000)·kappa·[1 + beta·(T_cell − 25)]`, `T_cell = T_a + 25·G/1000`.
* **Suspension**: 200 W while driving (four corners); **TEG**: 0.019 kWh/day spread evenly.
* **Auxiliary**: 250 W driving; parked `max(50, UA·((T_a − 30) + 15)/COP)` W when
  T_a > 28 °C (UA = 25 W/K, COP = 2.2), else 50 W standby. Annual-mean daily auxiliary
  energy at 50 km/day on the TMY: Phoenix 2.85, Lucknow 3.13, London 1.56 kWh; irradiance-
  weighted temperature factor f_T 0.909 / 0.906 / 0.997.
* **Battery**: whenever SoC would fall below 10 %, a grid charge restores 80 %; SoC is capped
  at 100 % (surplus harvest is curtailed). The year is run twice and the second pass, which
  starts from the first pass's end-of-year SoC, is reported (periodic steady state).
* **Mass feedback** (optional `m_over`): consumption is recomputed for a different vehicle
  mass; `pareto()` uses it so PV (3.5 kg/m²) and pack (2 kg/kWh) mass change demand.

Outputs: `fss = Σharvest / Σdemand`, `relief = (Σharvest − curtailed) / Σdemand` (≤ fss),
grid kWh, plug-ins, curtailment, SoC trace. Grid kWh is lumpy (plug-ins × refill size), so
relief is the robust measure of grid displacement.

`f_ss ≥ 1` is an annual ratio: winter plug-ins can remain because summer surplus cannot be
stored (e.g. Phoenix TMY at 15 m²: f_ss 1.06–1.12, one or two plug-ins per year).

### Sufficiency tiers (`classify()`)

| f_ss | Tier |
|---|---|
| ≥ 1.00 | self-sufficient |
| 0.90–1.00 | quasi-self-sufficient |
| 0.80–0.90 | highly solar-assisted |
| 0.50–0.80 | moderately solar-assisted |
| < 0.50 | grid-dependent |

## 6. Design inversion [III-E, V-C]

Neglecting the small TEG and suspension terms, f_ss ≥ 1 requires

    A·eta_pv·PSH·kappa·f_T ≥ D·c + E_aux          (c battery-side)

with `f_T` (`engine_fT()`) the irradiance-weighted annual temperature factor and `E_aux`
(`engine_Eaux()`) the annual-mean daily auxiliary energy, both from the same hourly engine:

    A_req = (D·c + E_aux) / (eta_pv·PSH·kappa·f_T)          # required_pv_area(..., climate=)
    D_max = (A·eta_pv·PSH·kappa·f_T − E_aux) / c            # max_selfsuff_km(..., climate=)

PSH, f_T and E_aux come from the climate passed in (`climate=None` = idealized synthetic;
`climate=load_city_tmy(city)` = satellite TMY). Scenario II, TMY: A_req 14.4 / 16.9 / 23.9 m²,
D_max 37.5 / 29.6 / 20.5 km/day (synthetic: 12.8 / 15.6 / 24.3 m²). Because TEG and suspension
are omitted, the closed form is slightly conservative: the full TMY simulation reaches
f_ss = 1 at ≈14.06 m² for Phoenix vs 14.4 m² from the formula.

## 7. Checks against satellite-derived resource data [V-B]

* `real_data_validation()` (Tier 1): replaces the assumed PSH and mean temperature with
  Global Solar Atlas GHI and air temperature.
* `tmy_validation()` (Tier 2): replaces the synthetic climate with the satellite hourly TMY.
* `gap_decomposition()`: magnitude = f_ss(synthetic) − f_ss(synthetic rescaled to the TMY's
  own annual GHI and mean temperature); distribution = that − f_ss(TMY). Using the TMY's own
  totals keeps the split clean even where databases disagree (Lucknow NSRDB GHI +6.8 % and
  mean T +1.9 °C vs Global Solar Atlas). Phoenix 0.058 + 0.047; Lucknow 0.030 + 0.027;
  London −0.030 + 0.022.
* `climate_error()`: monthly MAPE of the synthetic series vs TMY: 11.3 % / 12.9 % / 12.1 %.
* `tmy_robustness()`: Phoenix across NSRDB TMY-2022…2025: f_ss 0.832–0.840 (II), 0.419–0.422 (I).

## 8. Production-vehicle cross-validation [IV]

`validate()` runs the identical propulsion model with each car's published Cd, mass and an
estimated frontal area and Cr (eta_regen 0.65). References are battery-referenced (usable
pack ÷ rated range) to match the battery-side model output:

| Vehicle | Model | Reference | Basis |
|---|---|---|---|
| Lightyear 0 | 132 Wh/km | 96 Wh/km | 60 kWh / 625 km WLTP (certified grid-side figure: 105 Wh/km) |
| Aptera | 84 Wh/km | 65 Wh/km | 42 kWh / 400 mi (Launch Edition) |

## 9. Economics and multi-objective sweep [V-D, V-E]

* `economics(..., climate=)`: saved kWh = harvest actually used; residential tariffs
  (`PRICE`, unrounded): Phoenix 0.1576 USD/kWh (Arizona average price incl. fixed charges,
  EIA May 2025 via ACC); Lucknow 6.50 Rs/kWh ÷ 94.5975 Rs/USD (RBI reference rate 30 Jun 2026)
  = 0.0687 (UPPCL LMV-1 energy charge above 300 kWh/month, marginal); London 0.2632 GBP ×
  1.3373 USD/GBP (21 Oct 2026) = 0.3520 (Ofgem cap unit rate excl. VAT, waived to 31 Mar 2027;
  27.64 p with 5 % VAT). Paper Table V uses the TMY: payback 15.2 / 39.2 / 11.9 yr (full),
  7.1 / 18.3 / 5.6 yr (PV-only).
* Add-on cost 9560 USD; PV-only 4460 USD = 9560 − TEG 2500 − suspension 2000 − 600 (half
  of the wiring/structure/coatings item, which serves TEG and dampers).
* `pareto(..., climate=)`: PV area × pack size with mass feedback; synthetic climate averages
  4 weather seeds, TMY uses one year. Default sweep 8–20 m² × 150–300 kWh. Cost from the
  same PV basis as `economics()` (3060 USD / 11.6 m² ≈ 264 USD/m²) and 90 USD/kWh (assumed
  2030 solid-state pack price).
* `design_levers_tmy()`: Sec. V-D numbers on the TMY (κ sweep, κ for the quasi tier, η_regen
  0.72, suspension sweep, area for f_ss = 1, pack sweep).

## 10. Limitations

Statistics-matched (not certified) WLTP trace; two light reference vehicles; single-point
costs and tariffs on different bases; satellite-derived (not ground-measured) climate data; one representative year, no degradation; lumped cabin model; drive
converter losses inside `eta_dt`, MPPT and PV-side losses inside `kappa`; no route-level shading; numbers specific to one geometry.
