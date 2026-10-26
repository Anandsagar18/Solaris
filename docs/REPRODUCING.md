# Reproducing the ITEC-AP 2026 paper

```bash
python solaris.py > my_output.txt
diff my_output.txt results/reference_output.txt     # should print nothing
python make_figures.py
python -m pytest -q
```

"TMY" below means the satellite-derived hourly typical meteorological year shipped in
`data/<city>/` (NSRDB for Phoenix and Lucknow, PVGIS for London).

## Paper item → code

| Paper item | Content | Emitted by | Section of `solaris.py` output |
|---|---|---|---|
| Fig. 1 | Workflow diagram | drawn in LaTeX (TikZ) in `paper/` | — |
| Table I | Sufficiency tiers | `classify()` | — |
| Table II | Systems mass audit | `MASS`, `HARVEST_HW`, `M` | `1. MASS AUDIT` |
| Sec. III-B | 237 / 210 Wh/km (battery-side), reconstruction error | `whkm()`, `wltp_recon_error()` | `3. WLTP CONSUMPTION`, `WLTP RECONSTRUCTION ERROR` |
| Sec. III-C (TEG) | ΔT_leg, q_th, 0.019 kWh/day, 2.5-yr trade-off | `teg_daily_kwh()`, `teg_tradeoff()` | `2. TEG THERMAL NETWORK`, `TEG MASS-vs-OUTPUT TRADEOFF` |
| Sec. III-C (suspension) | 50–200 W sweep, Δf_ss ≈ 0.02 (TMY) | `design_levers_tmy()` | `DESIGN LEVERS ON THE SATELLITE TMY` |
| Table III | Lightyear 0 / Aptera cross-validation | `validate()` | `4. VALIDATION` |
| Table IV, "Synth." | Idealized-climate f_ss | `simulate()` | `5-8. 8760-h SIMULATION` |
| Table IV, "T1" | Global Solar Atlas annual | `real_data_validation()` | `REAL-DATA VALIDATION TIER 1` |
| Sec. V-B, Tier 1 text | GHI 2119.4 / 1725.6 / 1032.7, temps, GTI 7–17 % above GHI | `GSA` dictionary (from the `.xlsx` reports in `data/`) | — |
| Sec. V-B, Tier 2 text | TMY GHI vs GSA (−0.4 / +6.8 / +1.7 %), Lucknow +1.9 °C | `tmy_validation()` | `REAL-DATA VALIDATION TIER 2` |
| Table IV, "T2", plug-ins, relief | TMY | `tmy_validation()` | `REAL-DATA VALIDATION TIER 2` |
| Sec. V-B | Gap split (Phoenix 0.058 + 0.047) | `gap_decomposition()` | `GAP DECOMPOSITION` |
| Sec. V-B | TMY-release robustness (0.832–0.840) | `tmy_robustness()` | `TMY INTER-RELEASE ROBUSTNESS` |
| Sec. V-B | Monthly error 11.3 / 12.9 / 12.1 % | `climate_error()` | `SYNTHETIC CLIMATE ERROR` |
| Fig. 2 | SoC, idealized vs TMY | `make_figures.fig_soc_tmy()` | `figures/fig3_soc_tmy.*` |
| Sec. III-B (parked load), V-C (hot cities) | E_aux 2.85 / 3.13 / 1.56 kWh/day, f_T 0.909 / 0.906 / 0.997 (TMY) | `engine_Eaux(..., climate=)`, `engine_fT(..., climate=)` | — |
| Sec. V-C, Fig. 3 | A_req, D_max (TMY and idealized) | `required_pv_area(..., climate=)`, `max_selfsuff_km(..., climate=)`, `make_figures.fig_design()` | `6. DESIGN INVERSION`, `figures/fig5_design.*` |
| Sec. V-D | Area for f_ss = 1 (14.06 m²), pack sweep with mass feedback, κ sweep, κ for quasi (0.87), η_regen 0.72 | `design_levers_tmy()` | `DESIGN LEVERS ON THE SATELLITE TMY` |
| Sec. V-D | 8–20 m² × 150–300 kWh sweep on the TMY | `pareto(climate=load_city_tmy("Phoenix"))` | `8. MULTI-OBJECTIVE` |
| Table V | Relief, savings, tariffs, payback on the TMY | `economics(..., climate=)`, `COST_ITEMS`, `PRICE` | `7. ECONOMICS & GRID RELIEF` (rows "TMY"), `COST BREAKDOWN` |
| Plug-ins without solar | No-solar baseline | `tmy_validation()` (`charges_nosolar`) | `REAL-DATA VALIDATION TIER 2` |
| Fig. 4 | Code example | `README.md` "Using the toolkit" | — |

Repository-only figures: `fig1_wltp` (reconstructed trace), `fig2_soc_synthetic` (both
scenarios, idealized climate), `fig4_kappa` (κ sweep on the TMY), `fig6_econ` (relief and
payback on the TMY), `fig7_design_plane` (Phoenix TMY area × pack plane with mass feedback),
`fig8_monthly_ghi` (monthly GHI, idealized vs TMY).

## Environment used for the reference output

Python 3.13, numpy 2.5, matplotlib 3.11 (Linux). Results depend only on numpy's
`default_rng` seeding, which is stable across numpy ≥ 1.17.
