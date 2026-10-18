#!/usr/bin/env python3
"""PLANNING analysis for a possible NEW confirmatory study.

This is NOT inference. It performs no hypothesis tests on the existing data and
changes no frozen estimate. It only uses the existing 40-network differences as
a rough guide to variability for sample-size planning, and the study accounting
(Table 2 of paper_v4.md) for a crude compute extrapolation.

Dependencies: Python standard library + numpy.
Run:  python planning.py   (writes planning_results.json and planning_results.md
next to this file; reads ../source_data/*)
"""
import csv
import json
import math
import os
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source_data")
SEED = 20261017
REPS = 2000
N_GRID = [40, 80, 160, 320, 640]
REL_TARGETS = [0.10, 0.05, 0.025]          # fractions of nominal mean MSE
SCORE_TARGETS = [0.4, 0.2, 0.1]            # absolute score units (assumption, see md)
Z975 = 2.2414027276049473                  # two-sided 97.5% interval: z_{0.9875}
Z95 = 1.959963984540054                    # two-sided 95% interval: z_{0.975}


def read_csv(name):
    with open(os.path.join(SRC, name), newline="") as f:
        return list(csv.DictReader(f))


def summarize(x):
    x = np.asarray(x, float)
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    s = x.sum()
    i = int(np.argmax(np.abs(x)))
    return {
        "n": int(x.size),
        "n_exact_zero": int((x == 0).sum()),
        "mean": float(x.mean()),
        "sd": float(x.std(ddof=1)),
        "median": med,
        "mad": mad,
        "robust_sd_1.4826_mad": 1.4826 * mad,
        "sum": float(s),
        "max_abs_index": i,
        "max_abs_value": float(x[i]),
        "max_share_of_sum_abs": float(abs(x[i]) / np.abs(x).sum()),
        "max_signed_share_of_summed_difference": float(x[i] / s) if s != 0 else None,
        "sd_without_most_influential": float(np.delete(x, i).std(ddof=1)),
        "mean_without_most_influential": float(np.delete(x, i).mean()),
    }


def normal_n(sd, target, z):
    return int(math.ceil((z * sd / target) ** 2))


def boot_halfwidth(pop, n, z_level, rng, reps=REPS):
    """Resample n networks with replacement from the empirical differences,
    take the mean, repeat `reps` times; half-width of the central percentile
    interval of those resampled means."""
    alpha = (1 - z_level) / 2 * 100
    idx = rng.integers(0, len(pop), size=(reps, n))
    means = pop[idx].mean(axis=1)
    lo, hi = np.percentile(means, [alpha, 100 - alpha])
    return float((hi - lo) / 2)


def plan_block(label, diffs, targets, level_z, level_pct, target_units, ref_scale):
    out = {"label": label, "interval_level": level_pct, "target_units": target_units,
           "reference_scale": ref_scale, "targets_absolute": targets}
    s = summarize(diffs)
    out["summary"] = s
    d = np.asarray(diffs, float)
    drop = np.delete(d, s["max_abs_index"])
    scen = {"observed_sd": (d, s["sd"]), "excl_top_network": (drop, s["sd_without_most_influential"])}
    rng = np.random.default_rng(SEED)
    for name, (pop, sd) in scen.items():
        res = {"sd_used": sd, "normal_required_n": {}, "bootstrap_halfwidth": {},
               "normal_halfwidth": {}, "bootstrap_min_grid_n": {}}
        for t in targets:
            res["normal_required_n"][repr(t)] = normal_n(sd, t, level_z)
        for n in N_GRID:
            res["normal_halfwidth"][str(n)] = float(level_z * sd / math.sqrt(n))
            res["bootstrap_halfwidth"][str(n)] = boot_halfwidth(pop, n, level_pct / 100, rng)
        for t in targets:
            ok = [n for n in N_GRID if res["bootstrap_halfwidth"][str(n)] <= t]
            res["bootstrap_min_grid_n"][repr(t)] = ok[0] if ok else ">640"
        out[name] = res
    return out


def main():
    prim = read_csv("holdout_primary_paired.csv")
    met = read_csv("holdout_network_metrics.csv")
    fc = read_csv("fig3_networks.csv")

    def nominal_mse(method):
        v = [float(r["mse"]) for r in met if r["condition"] == "broad"
             and r["pool"] == "exclude_endpoints" and r["budget"] == "3" and r["method"] == method]
        assert len(v) == 40
        return float(np.mean(v))

    results = {
        "status": "PLANNING ONLY. Not inference. No tests run; no frozen estimate changed.",
        "seed": SEED, "bootstrap_reps": REPS, "n_grid": N_GRID,
        "method_note": ("Normal approx: n = ceil((z*SD/h)^2), z=2.2414 (97.5%) or 1.96 (95%). "
                       "Bootstrap: resample n networks with replacement from the 40 (or 39) "
                       "observed differences, take the mean, repeat 2000 times; half-width = half the "
                       "central percentile interval (1.25-98.75% or 2.5-97.5%) of those means. "
                       "It is a plug-in sampling-distribution width, not a nested bootstrap CI."),
        "caveat": ("Heavy tails: a handful of networks carry much of the summed difference, so SDs from 40 "
                   "networks are unstable, the normal approximation is optimistic, and the bootstrap "
                   "cannot generate tail behaviour that was not among the 40 observed networks "
                   "(also optimistic). Excluding the top network is a sensitivity range, not an estimate."),
        "primary": [],
    }
    for contrast, nominal in [("ensemble_scalar - local_scalar", "local_scalar"),
                              ("ensemble_vector - local_vector", "local_vector")]:
        rows = sorted((r for r in prim if r["contrast"] == contrast), key=lambda r: int(r["network_id"]))
        d = [float(r["paired_mse_difference"]) for r in rows]
        nm = nominal_mse(nominal)
        targets = [f * nm for f in REL_TARGETS]
        blk = plan_block(contrast, d, targets, Z975, 97.5, "q^2 (raw response MSE)", {
            "nominal_method": nominal, "nominal_mean_mse": nm, "relative_targets": REL_TARGETS})
        results["primary"].append(blk)
    d = [float(r["score_difference"]) for r in sorted(fc, key=lambda r: int(r["network_id"]))]
    results["forecast"] = plan_block(
        "forecast score difference (ensemble - nominal, LS, broad, excl. endpoints, M=3)", d,
        SCORE_TARGETS, Z95, 95.0, "score units (log-score; unitless)",
        {"note": "Targets are absolute half-widths 0.4/0.2/0.1; MSE-relative targets do not apply. "
                 "For orientation only: observed mean difference and its frozen 95% CI half-width ~0.59."})

    # (c) compute scaling, Table 2
    stages = [
        ("Development", 8, 19200, 5696, 25.4, "12-unit"),
        ("Frozen recording evaluation", 40, 129600, 38610, 356.0, "12-unit"),
        ("Independent forecast study", 40, 6480, 3006, 17.5, "12-unit"),
        ("Exploratory 100-unit family", 8, 3072, 1436, 693.1, "100-unit"),
    ]
    comp = []
    for name, J, rec, calls, sec, unit in stages:
        per_net = sec / J
        row = {"stage": name, "setting": unit, "independent_J": J, "evaluation_records": rec,
               "map_calls": calls, "runtime_s": sec,
               "s_per_record": sec / rec, "s_per_network": per_net, "s_per_map_call": sec / calls,
               "records_per_network": rec / J, "map_calls_per_network": calls / J,
               "EXTRAPOLATION_wall_s": {str(n): per_net * n for n in (160, 640)}}
        comp.append(row)
    results["compute"] = {
        "label": ("EXTRAPOLATION, not measurement: wall time = n * (stage seconds per network), i.e. "
                  "linear in networks with the stage's own per-network design (truths x noises x readouts, "
                  "conditions, methods). Ignores parallelism, memory, solver-difficulty changes and "
                  "different designs; the 100-unit stage has only 8 networks and a different model family."),
        "stages": comp}

    with open(os.path.join(HERE, "planning_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    with open(os.path.join(HERE, "planning_results.md"), "w") as f:
        f.write(render_md(results))


def fmt(x):
    return f"{x:.3g}"


def hms(s):
    return f"{s:.0f} s" if s < 600 else f"{s/60:.1f} min" if s < 7200 else f"{s/3600:.2f} h"


def render_md(R):
    L = []
    L.append("# Planning analysis for a possible new confirmatory study\n")
    L.append("**PLANNING ONLY, not inference.** No hypothesis tests were run on the existing data and no frozen "
             "estimate was changed. The 40 existing network-level differences are used only as a rough guide to "
             "variability. Script: `planning.py` (numpy only, seed %d); machine-readable output: `planning_results.json`.\n" % R["seed"])
    L.append("## (a) Spread of the paired network differences (n = 40 each)\n")
    L.append("| Quantity | ES-LS (q^2) | EV-LV (q^2) | Forecast score diff |\n|---|---:|---:|---:|")
    blks = R["primary"] + [R["forecast"]]
    for key, lab in [("mean", "Mean"), ("sd", "SD"), ("median", "Median"),
                     ("robust_sd_1.4826_mad", "Robust SD (1.4826 x MAD)"),
                     ("max_share_of_sum_abs", "Max single-network share of sum of absolute differences"),
                     ("max_signed_share_of_summed_difference", "Top network's signed share of the summed difference"),
                     ("sd_without_most_influential", "SD without most influential network"),
                     ("n_exact_zero", "Networks with exactly zero difference (of 40)")]:
        L.append(f"| {lab} | " + " | ".join(fmt(b["summary"][key]) for b in blks) + " |")
    L.append("\nSD far above the robust SD and a large top-network share indicate heavy tails. "
             "The signed share can exceed 1 when positive and negative differences cancel in the sum. A robust SD near zero "
             "reflects many networks where the two designs choose the same recording set (difference exactly 0), "
             "so it is not a usable planning SD. The bootstrap grid starts at n = 40, so a minimum of 40 only means the target is met at the smallest n examined.\n")
    L.append("## (b) Planning sample sizes for a NEW study\n")
    L.append("Target: expected half-width of the paired interval at most 10%, 5%, 2.5% of the nominal mean MSE "
             "(97.5% interval, primary comparisons). Forecast: 95% interval; MSE-relative targets do not apply, so "
             "absolute half-widths of 0.4, 0.2, 0.1 score units are used (an assumption). "
             "Networks needed by the normal approximation, then the bootstrap half-width by n.\n")
    for b in blks:
        L.append(f"### {b['label']}\n")
        ref = b["reference_scale"]
        if "nominal_mean_mse" in ref:
            L.append(f"Nominal ({ref['nominal_method']}) mean MSE = {fmt(ref['nominal_mean_mse'])} q^2.\n")
        tg = b["targets_absolute"]
        names = (["10%", "5%", "2.5%"] if "nominal_mean_mse" in ref else ["0.4", "0.2", "0.1"])
        L.append("| Scenario | Method | " + " | ".join(f"h<={nm} ({fmt(t)})" for nm, t in zip(names, tg)) + " |")
        L.append("|---|---|" + "---:|" * 3)
        for sc, scl in [("observed_sd", "observed SD"), ("excl_top_network", "top network excluded")]:
            r = b[sc]
            L.append(f"| {scl} (SD {fmt(r['sd_used'])}) | Normal: n required | " +
                     " | ".join(str(r["normal_required_n"][repr(t)]) for t in tg) + " |")
            L.append(f"| {scl} | Bootstrap: smallest grid n | " +
                     " | ".join(str(r["bootstrap_min_grid_n"][repr(t)]) for t in tg) + " |")
        L.append("")
        L.append("| n | " + " | ".join(f"{s} {m}" for s in ("obs", "excl") for m in ("normal", "boot")) + " |")
        L.append("|---:|" + "---:|" * 4)
        for n in N_GRID:
            o, e = b["observed_sd"], b["excl_top_network"]
            L.append(f"| {n} | {fmt(o['normal_halfwidth'][str(n)])} | {fmt(o['bootstrap_halfwidth'][str(n)])} | "
                     f"{fmt(e['normal_halfwidth'][str(n)])} | {fmt(e['bootstrap_halfwidth'][str(n)])} |")
        L.append("\nHalf-widths in " + b["target_units"] + ".\n")
    L.append("**Caution.** " + R["caveat"] + " Treat these n values as lower-bound, order-of-magnitude "
             "guides. " + R["method_note"] + "\n")
    L.append("## (c) Computational scaling (from Table 2 study accounting)\n")
    L.append("| Stage | Setting | J | Records | MAP calls | Runtime (s) | s/record | s/network | s/MAP call |\n|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for s in R["compute"]["stages"]:
        L.append(f"| {s['stage']} | {s['setting']} | {s['independent_J']} | {s['evaluation_records']:,} | {s['map_calls']:,} | "
                 f"{s['runtime_s']} | {s['s_per_record']:.2e} | {s['s_per_network']:.3g} | {s['s_per_map_call']:.2e} |")
    L.append("\n**Extrapolation (not measured):** " + R["compute"]["label"] + "\n")
    L.append("| Stage | Setting | 160 networks | 640 networks |\n|---|---|---:|---:|")
    for s in R["compute"]["stages"]:
        w = s["EXTRAPOLATION_wall_s"]
        L.append(f"| {s['stage']} | {s['setting']} | {hms(w['160'])} | {hms(w['640'])} |")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    main()
