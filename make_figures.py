#!/usr/bin/env python3
"""Regenerate every SOLARIS figure into figures/ (deterministic; needs matplotlib).

    python make_figures.py            # all figures, PNG (300 dpi) + PDF (vector)

Paper figures (ITEC-AP 2026): fig3_soc_tmy (Fig. 2), fig5_design (Fig. 3).
Fig. 1 is drawn in LaTeX (TikZ); fig7_design_plane and fig4_kappa back Sec. V-D.
The rest are repository/supplementary figures.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import solaris as S

OUT = os.path.join(S.HERE, "figures")
os.makedirs(OUT, exist_ok=True)

# Fixed colour per city (entity), never per rank. Validated categorical slots
# (light surface): ΔE_CVD >= 9.2 between adjacent pairs; panels are also labelled.
CITY_COLOR = {"Phoenix": "#eb6834", "Lucknow": "#1baf7a", "London": "#2a78d6"}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#d9d8d2"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "TeX Gyre Termes", "DejaVu Serif"],
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "mathtext.fontset": "stix", "font.size": 8, "axes.titlesize": 8,
    "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 6.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.6,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
COL_W = 3.45  # IEEE single-column width (in)


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"))
    plt.close(fig)
    print("  wrote figures/%s.{png,pdf}" % name)


def _days(soc):
    return np.arange(len(soc)) / 24.0


def fig_wltp():
    v = S.wltp_trace() * 3.6
    fig, ax = plt.subplots(figsize=(COL_W, 1.6))
    ax.plot(np.arange(len(v)), v, lw=0.8, color=CITY_COLOR["London"])
    ax.set_xlabel("Time (s)"); ax.set_ylabel("Speed (km/h)")
    ax.set_xlim(0, len(v)); ax.set_ylim(0, 140); ax.grid(color=GRID, lw=0.4)
    _save(fig, "fig1_wltp")


def fig_soc_synthetic():
    fig, axs = plt.subplots(2, 1, figsize=(COL_W, 3.6), sharex=True)
    for ax, (km, city, title) in zip(axs, [(50, True, "Scenario II: 50 km/day urban"),
                                            (100, False, "Scenario I: 100 km/day mixed")]):
        for loc in S.LOCS:
            r = S.simulate(loc, km, city)
            ax.plot(_days(r["soc"]), r["soc"], lw=0.5, color=CITY_COLOR[loc],
                    label=f"{loc}: $f_{{ss}}$={r['fss']:.2f}, {r['charges']}/yr")
        ax.axhline(10, color=MUTED, lw=0.5, ls=":")
        ax.set_ylim(0, 105); ax.set_ylabel("SoC (%)"); ax.set_title(title)
        ax.legend(loc="lower center", frameon=False, ncol=1)
    axs[-1].set_xlabel("Day of year"); axs[-1].set_xlim(0, 365)
    _save(fig, "fig2_soc_synthetic")


def fig_soc_tmy():
    """PAPER FIG.: synthetic vs satellite-derived hourly TMY, Scenario II, all three cities."""
    src = {"Phoenix": "NSRDB", "Lucknow": "NSRDB", "London": "PVGIS"}
    fig, axs = plt.subplots(3, 1, figsize=(COL_W, 3.9), sharex=True)
    for ax, loc in zip(axs, S.LOCS):
        syn = S.simulate(loc, 50, True)
        mea = S.simulate(loc, 50, True, climate=S.load_city_tmy(loc))
        c = CITY_COLOR[loc]
        ax.plot(_days(syn["soc"]), syn["soc"], lw=0.5, color=c, alpha=0.45, ls="--")
        ax.plot(_days(mea["soc"]), mea["soc"], lw=0.6, color=c)
        ax.axhline(10, color=MUTED, lw=0.5, ls=":")
        ax.set_ylim(0, 132); ax.set_yticks([0, 50, 100]); ax.set_ylabel("SoC (%)")
        ax.text(0.01, 0.97, loc, transform=ax.transAxes, va="top", ha="left",
                fontsize=8, fontweight="bold", color=INK)
        ax.text(0.99, 0.97, f"$f_{{ss}}$ {syn['fss']:.2f} ({syn['charges']}/yr) synthetic"
                f" $\\rightarrow$ {mea['fss']:.2f} ({mea['charges']}/yr) {src[loc]}",
                transform=ax.transAxes, va="top", ha="right", fontsize=6.3, color=INK)
    axs[0].plot([], [], lw=0.6, color=MUTED, ls="--", alpha=0.6, label="idealized synthetic climate")
    axs[0].plot([], [], lw=0.8, color=MUTED, label="satellite-derived hourly TMY")
    axs[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    axs[-1].set_xlabel("Day of year"); axs[-1].set_xlim(0, 365)
    fig.subplots_adjust(hspace=0.10)
    _save(fig, "fig3_soc_tmy")


def fig_kappa():
    """kappa_pv sensitivity on the satellite-derived TMY (Scenario II)."""
    ks = np.linspace(0.55, 0.95, 17)
    fig, ax = plt.subplots(figsize=(COL_W, 1.9))
    ax.axvspan(0.60, 0.80, color=GRID, alpha=0.35, lw=0)
    ax.text(0.70, 0.31, "range swept in the paper", fontsize=6, color=MUTED, ha="center")
    for y, lab, x, ha in [(0.9, "quasi-self-sufficient", 0.555, "left"),
                          (0.8, "highly solar-assisted", 0.555, "left"),
                          (0.5, "moderately solar-assisted", 0.70, "center")]:
        ax.axhline(y, color=MUTED, lw=0.5, ls=":")
        ax.text(x, y + 0.01, lab, fontsize=6, color=MUTED, ha=ha)
    for loc in S.LOCS:
        t = S.load_city_tmy(loc)
        f = [S.simulate(loc, 50, True, kappa=k, climate=t)["fss"] for k in ks]
        ax.plot(ks, f, lw=1.6, color=CITY_COLOR[loc])
        ax.text(0.945, f[-1] + 0.02, loc, fontsize=7, color=INK, ha="right")
    ax.set_xlabel(r"PV real-world derating $\kappa_{pv}$"); ax.set_ylabel(r"$f_{ss}$ (Scen. II, TMY)")
    ax.set_xlim(0.55, 0.95); ax.set_ylim(0.3, 1.1)
    _save(fig, "fig4_kappa")


def fig_design():
    """PAPER FIG.: design nomograph on the satellite-derived TMY (solid) with the
    idealized synthetic climate for comparison (dashed)."""
    A = np.linspace(8, 30, 45)
    fig, ax = plt.subplots(figsize=(COL_W, 2.0))
    for loc, (xl, dy, which) in zip(S.LOCS, ((18.0, 5, "syn"), (24.0, -9, "tmy"), (22.0, -9, "tmy"))):
        t = S.load_city_tmy(loc)
        d = np.array([S.max_selfsuff_km(loc, True, climate=t, A=a) for a in A])
        ds = np.array([S.max_selfsuff_km(loc, True, A=a) for a in A])
        ax.plot(A, ds, lw=0.8, ls="--", color=CITY_COLOR[loc], alpha=0.6)
        ax.plot(A, d, lw=1.6, color=CITY_COLOR[loc])
        yref = ds if which == "syn" else d
        ax.text(xl, float(np.interp(xl, A, yref)) + dy, loc, fontsize=7, color=INK, ha="left")
        d0 = S.max_selfsuff_km(loc, True, climate=t)
        ax.plot([S.A_skin], [d0], "o", ms=4, color=CITY_COLOR[loc], mec="white", mew=0.8, zorder=3)
        ax.text(S.A_skin - 0.3, d0, f"{d0:.1f}", fontsize=6, color=INK, ha="right", va="center")
    for y in (50, 100):
        ax.axhline(y, color=MUTED, lw=0.5, ls=":")
        ax.text(8.2, y + 2, f"{y} km/day", fontsize=6, color=MUTED, ha="left")
    ax.axvline(S.A_skin, color=INK, lw=0.7, ls="--")
    ax.text(S.A_skin + 0.3, 122, "as-built 11.6 m$^2$", fontsize=6, color=INK)
    ax.plot([], [], lw=1.6, color=MUTED, label="satellite TMY")
    ax.plot([], [], lw=0.8, ls="--", color=MUTED, label="idealized climate")
    ax.legend(frameon=False, loc="lower right", fontsize=6)
    ax.set_xlabel("PV skin area (m$^2$)"); ax.set_ylabel("Max self-sufficient\ndistance (km/day)")
    ax.set_xlim(8, 30); ax.set_xticks(range(8, 31, 2)); ax.set_ylim(0, 132)
    ax.grid(color=GRID, lw=0.4); ax.set_axisbelow(True)
    _save(fig, "fig5_design")


def fig_econ():
    locs = list(S.LOCS); x = np.arange(len(locs))
    e = [S.economics(l, 50, True, climate=S.load_city_tmy(l)) for l in locs]
    fig, axs = plt.subplots(1, 2, figsize=(COL_W, 1.8))
    axs[0].bar(x, [d["grid_relief_pct"] for d in e], color=[CITY_COLOR[l] for l in locs], width=0.6)
    axs[0].set_ylabel("Grid-energy relief (%)"); axs[0].set_ylim(0, 100)
    axs[1].bar(x - 0.17, [d["payback_yr"] for d in e], width=0.32, color=MUTED, label="full system")
    axs[1].bar(x + 0.17, [d["payback_pvonly"] for d in e], width=0.32,
               color=[CITY_COLOR[l] for l in locs], label="PV-only")
    axs[1].set_ylabel("Simple payback (yr)"); axs[1].legend(frameon=False, fontsize=6)
    for ax in axs:
        ax.set_xticks(x); ax.set_xticklabels(locs, fontsize=6.5); ax.grid(axis="y", color=GRID, lw=0.4)
        ax.set_axisbelow(True)
    fig.tight_layout()
    _save(fig, "fig6_econ")


def fig_design_plane():
    """Repository figure backing paper Sec. V-D: Phoenix II on the satellite-derived TMY. Shading: annual grid energy;
    lines: f_ss iso-lines. Pack mass (2 kg/kWh) and PV mass (3.5 kg/m^2) feed back into
    consumption, so f_ss falls slightly as the pack grows."""
    t = S.load_city_tmy("Phoenix")
    A = np.array([8, 9, 10, 11, 11.6, 12, 13, 14, 15, 16, 17.5, 20])
    C = np.array([150, 175, 200, 225, 250, 275, 300])
    grid = np.zeros((len(C), len(A))); fss = np.zeros((len(C), len(A)))
    for j, a in enumerate(A):
        for i, cap in enumerate(C):
            m = (S.M["P0"] - 500 - 41) + a * 3.5 + cap * 2.0
            r = S.simulate("Phoenix", 50, True, A_over=a, cap_over=cap, m_over=m, climate=t)
            grid[i, j] = r["grid_kwh"]; fss[i, j] = r["fss"]
    fig, ax = plt.subplots(figsize=(COL_W, 2.2))
    levels = np.arange(0, 2001, 200)
    cf = ax.contourf(A, C, grid, levels=levels, cmap="Blues_r", extend="max")
    cb = fig.colorbar(cf, ax=ax, pad=0.02); cb.set_label("Grid energy (kWh/yr)"); cb.ax.tick_params(labelsize=6)
    cs = ax.contour(A, C, fss, levels=[0.8, 0.9, 1.0], colors=INK, linewidths=0.8,
                    linestyles=[":", "--", "-"])
    ax.clabel(cs, fmt=lambda v: f"$f_{{ss}}$={v:.1f}", fontsize=6)
    ax.plot([S.A_skin], [250], "o", ms=5, color="#eb6834", mec="white", mew=1.0)
    ax.annotate("demonstrator", (S.A_skin, 250), xytext=(8.3, 280), fontsize=6, color=INK,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
    ax.set_xlabel("PV skin area (m$^2$)"); ax.set_ylabel("Pack capacity (kWh)")
    _save(fig, "fig7_design_plane")


def fig_monthly_ghi():
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 1.9), sharey=True)
    mh = np.minimum(((np.arange(8760) // 24) / 30.44).astype(int), 11)
    for ax, loc in zip(axs, S.LOCS):
        e = S.climate_error(loc)
        m = np.arange(1, 13)
        ax.plot(m, e["meas"], "-o", ms=3, lw=1.4, color=CITY_COLOR[loc], label="satellite TMY")
        ax.plot(m, e["syn"], "--", lw=1.2, color=MUTED, label="synthetic")
        ax.set_title(f"{loc} (MAPE {e['monthly_mape']:.1f}%)"); ax.set_xticks([1, 4, 7, 10])
        ax.set_xlabel("Month"); ax.grid(color=GRID, lw=0.4)
    axs[0].set_ylabel("GHI (kWh/m$^2$/day)"); axs[0].legend(frameon=False)
    fig.tight_layout()
    _save(fig, "fig8_monthly_ghi")


if __name__ == "__main__":
    print("SOLARIS", S.__version__, "- regenerating figures")
    fig_wltp(); fig_soc_synthetic(); fig_soc_tmy(); fig_kappa()
    fig_design(); fig_econ(); fig_design_plane(); fig_monthly_ghi()
