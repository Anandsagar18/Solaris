"""Regression tests: every headline number in the ITEC-AP 2026 paper.

Run from the repository root:  python -m pytest -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import solaris as S  # noqa: E402


def test_mass_audit():
    assert S.HARVEST_HW == 182
    assert S.M["P0"] == 2482 and S.M["PA"] == 2696


def test_teg_is_negligible():
    assert S.E_TEG == pytest.approx(0.019, abs=1e-3)
    assert S.TEG["dT_leg"] == pytest.approx(3.77, abs=0.01)
    assert S.TEG["q_through"] == pytest.approx(565.0, abs=0.5)


def test_wltp_consumption_and_reconstruction():
    assert round(S.whkm("P0")) == 237 and round(S.whkm("P0", city=True)) == 210
    assert round(S.whkm("P0", eta_regen=0.72)) == 226
    assert S.wltp_recon_error()["TOTAL"]["dist_err"] == pytest.approx(0.11, abs=0.01)


def test_production_vehicle_validation():
    v = S.validate()
    assert v["Lightyear0"]["model_whkm"] == 132 and v["Aptera"]["model_whkm"] == 84


@pytest.mark.parametrize("loc,km,city,fss,charges", [
    ("Phoenix", 50, True, 0.94, 6), ("Lucknow", 50, True, 0.77, 7), ("London", 50, True, 0.51, 12),
    ("Phoenix", 100, False, 0.47, 29), ("Lucknow", 100, False, 0.39, 33), ("London", 100, False, 0.24, 39),
])
def test_synthetic_base_case(loc, km, city, fss, charges):
    r = S.simulate(loc, km, city)
    assert round(r["fss"], 2) == fss and r["charges"] == charges
    assert r["relief"] <= r["fss"] + 1e-9


def test_no_double_drivetrain_efficiency():
    # demand must use battery-side Wh/km directly (v1.0.x divided by eta_dt twice)
    r = S.simulate("Phoenix", 50, True, pv_scale=0.0)
    prop = 50 * 365 * S.whkm("P0", city=True) / 1000.0
    assert prop < r["ann_dem"] < prop + 3000          # + auxiliaries only


def test_tier1_satellite_annual():
    got = {(r["scenario"], r["city"]): r["f_real"] for r in S.real_data_validation()}
    assert got[("II 50km", "Phoenix")] == 0.88
    assert got[("II 50km", "Lucknow")] == 0.72
    assert got[("II 50km", "London")] == 0.53


@pytest.mark.skipif(not all(os.path.exists(p) for p in S.TMY_FILES.values()),
                    reason="TMY files not present under data/")
def test_tier2_satellite_tmy():
    got = {(r["scenario"], r["city"]): r for r in S.tmy_validation()}
    assert got[("II 50km", "Phoenix")]["f_tmy"] == 0.83
    assert got[("II 50km", "Lucknow")]["f_tmy"] == 0.71
    assert got[("II 50km", "London")]["f_tmy"] == 0.52
    assert got[("I 100km", "Phoenix")]["f_tmy"] == 0.42
    assert got[("II 50km", "Phoenix")]["charges"] == 5
    assert got[("II 50km", "Phoenix")]["charges_nosolar"] == 27
    assert got[("II 50km", "Phoenix")]["relief_pct"] == 82
    for r in got.values():
        assert r["relief_pct"] <= round(100 * r["f_tmy"]) + 1


@pytest.mark.skipif(not all(os.path.exists(p) for p in S.TMY_RELEASES.values()),
                    reason="Phoenix TMY releases not present under data/")
def test_tmy_release_robustness():
    f = [r["fss"] for r in S.tmy_robustness() if r["scenario"] == "II 50km"]
    assert min(f) >= 0.83 and max(f) <= 0.841


def test_design_inversion():
    t = S.load_city_tmy("Phoenix")
    assert round(S.required_pv_area(50, True, "Phoenix", climate=t), 1) == 14.4
    assert round(S.max_selfsuff_km("Phoenix", True, climate=t), 1) == 37.5
    assert round(S.required_pv_area(50, True, "London", climate=S.load_city_tmy("London")), 1) == 23.9
    assert round(S.required_pv_area(50, True, "Phoenix"), 1) == 12.8     # idealized climate


def test_mass_feedback_in_pareto():
    rows = S.pareto("Phoenix", 50, True, climate=S.load_city_tmy("Phoenix"),
                    areas=(11.6,), caps=(150, 250))
    assert rows[0]["fss"] > rows[1]["fss"]           # heavier pack -> lower f_ss


def test_economics():
    e = S.economics("Phoenix", 50, True, climate=S.load_city_tmy("Phoenix"))
    assert round(e["grid_relief_pct"]) == 82 and round(e["payback_yr"], 1) == 15.2
    assert S.SYSTEM_COST == 9560 and round(S.PV_ONLY_COST) == 4460
    assert abs(S.PRICE["London"] - 0.2632 * 1.3373) < 1e-12


def test_paper_listing_output():
    # Fig. 4 of the paper prints (0.83, 5): results must be plain Python numbers
    t = S.load_city_tmy("Phoenix")
    r = S.simulate("Phoenix", 50, True, climate=t)
    assert repr((round(r["fss"], 2), r["charges"])) == "(0.83, 5)"
    assert isinstance(S.required_pv_area(50, True, "Phoenix", climate=t), float)


def test_pareto_cost_basis_and_range():
    rows = S.pareto("Phoenix", 50, True, climate=S.load_city_tmy("Phoenix"), areas=(11.6,))
    assert [r["cap"] for r in rows] == [150, 200, 250, 300]
    # PV priced on the same basis as economics(): 3060 USD for the 11.6 m^2 skin
    assert rows[0]["cost"] == pytest.approx(3060 + 150 * 90.0)
