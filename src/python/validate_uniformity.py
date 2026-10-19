#!/usr/bin/env python3
"""Validate sphere-surface sampling: radius check + u=z/R uniformity."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_points(path: Path) -> np.ndarray:
    points = np.loadtxt(path)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected N x 3 point file, got shape {points.shape}")
    return points


def radius_stats(points: np.ndarray) -> dict[str, float]:
    radii = np.linalg.norm(points, axis=1)
    return {
        "mean_radius": float(radii.mean()),
        "std_radius": float(radii.std()),
        "min_radius": float(radii.min()),
        "max_radius": float(radii.max()),
        "max_abs_dev": float(np.max(np.abs(radii - radii.mean()))),
    }


def chi_square_uniform_u(u: np.ndarray, n_bins: int = 20) -> dict[str, float]:
    """Pearson chi-square of u against Uniform[-1, 1]."""
    counts, _ = np.histogram(u, bins=n_bins, range=(-1.0, 1.0))
    expected = len(u) / n_bins
    chi2 = float(np.sum((counts - expected) ** 2 / expected))
    dof = n_bins - 1
    # Regularized upper incomplete gamma survival for chi2 CDF complement.
    # Using Wilson–Hilferty normal approximation for a lightweight p-value.
    z = ((chi2 / dof) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * dof))) / math.sqrt(
        2.0 / (9.0 * dof)
    )
    p_approx = 0.5 * math.erfc(z / math.sqrt(2.0))
    return {
        "chi2": chi2,
        "dof": float(dof),
        "chi2_over_dof": chi2 / dof,
        "p_approx": float(p_approx),
        "mad_from_uniform": float(np.mean(np.abs(counts - expected)) / expected),
    }


def analyze(points: np.ndarray, radius: float | None = None) -> dict:
    stats = radius_stats(points)
    r = float(radius) if radius is not None else stats["mean_radius"]
    u = points[:, 2] / r
    u = np.clip(u, -1.0, 1.0)
    uniformity = chi_square_uniform_u(u)
    return {
        "n_points": int(len(points)),
        "radius_nominal": r,
        "radius": stats,
        "u_mean": float(u.mean()),
        "u_std": float(u.std()),
        "uniformity": uniformity,
    }


def plot_comparison(
    equal_area: np.ndarray,
    naive: np.ndarray,
    radius: float,
    output: Path,
    n_bins: int = 20,
) -> None:
    u_eq = np.clip(equal_area[:, 2] / radius, -1.0, 1.0)
    u_nv = np.clip(naive[:, 2] / radius, -1.0, 1.0)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=120)

    for ax, u, title in (
        (axes[0], u_eq, "Equal-area: $u=z/R$"),
        (axes[1], u_nv, "Naive $\\theta$: $u=z/R$"),
    ):
        ax.hist(u, bins=n_bins, range=(-1.0, 1.0), density=True, color="#2a6f7a", alpha=0.85)
        ax.axhline(0.5, color="#b35c38", linestyle="--", linewidth=1.5, label="Uniform density")
        ax.set_xlim(-1.0, 1.0)
        ax.set_xlabel("$u = z/R$")
        ax.set_ylabel("Density")
        ax.set_title(title)
        ax.legend(frameon=False, loc="upper center")

    fig.suptitle(
        f"Surface measure check (N={len(equal_area)}, R={radius:g})",
        fontsize=12,
    )
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate radius and u=z/R uniformity for sphere samples."
    )
    parser.add_argument(
        "--equal-area",
        type=Path,
        required=True,
        help="Point file from equal-area sampling",
    )
    parser.add_argument(
        "--naive",
        type=Path,
        default=None,
        help="Optional point file from naive theta sampling (for contrast plot)",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=None,
        help="Nominal sphere radius (default: inferred from equal-area mean)",
    )
    parser.add_argument(
        "--figure",
        type=Path,
        default=Path("results/uniformity.png"),
        help="Comparison histogram output path",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/uniformity.json"),
        help="JSON metrics output path",
    )
    parser.add_argument(
        "--max-radius-error",
        type=float,
        default=1e-8,
        help="Fail if max |||p||-R| exceeds this",
    )
    parser.add_argument(
        "--max-chi2-over-dof",
        type=float,
        default=2.0,
        help="Fail equal-area check if chi2/dof exceeds this",
    )
    parser.add_argument(
        "--min-naive-chi2-over-dof",
        type=float,
        default=5.0,
        help="When --naive is set, fail if naive chi2/dof is below this",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    equal_area = load_points(args.equal_area)
    radius = args.radius if args.radius is not None else float(
        np.linalg.norm(equal_area, axis=1).mean()
    )

    report = {"equal_area": analyze(equal_area, radius)}

    eq_spread = report["equal_area"]["radius"]["max_abs_dev"]
    eq_bias = abs(report["equal_area"]["radius"]["mean_radius"] - radius)
    eq_chi = report["equal_area"]["uniformity"]["chi2_over_dof"]

    failures: list[str] = []
    if eq_spread > args.max_radius_error:
        failures.append(
            f"equal-area radius spread {eq_spread:.3e} > {args.max_radius_error:.3e}"
        )
    if eq_bias > args.max_radius_error:
        failures.append(
            f"equal-area mean radius bias {eq_bias:.3e} > {args.max_radius_error:.3e}"
        )
    if eq_chi > args.max_chi2_over_dof:
        failures.append(
            f"equal-area chi2/dof {eq_chi:.3f} > {args.max_chi2_over_dof:.3f}"
        )

    if args.naive is not None:
        naive = load_points(args.naive)
        report["naive"] = analyze(naive, radius)
        nv_chi = report["naive"]["uniformity"]["chi2_over_dof"]
        if nv_chi < args.min_naive_chi2_over_dof:
            failures.append(
                f"naive chi2/dof {nv_chi:.3f} < {args.min_naive_chi2_over_dof:.3f} "
                "(expected strong departure from Uniform[-1,1])"
            )
        plot_comparison(equal_area, naive, radius, args.figure)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps(report, indent=2))
    print(f"Wrote report to {args.report}")
    if args.naive is not None:
        print(f"Wrote figure to {args.figure}")

    if failures:
        for msg in failures:
            print(f"FAIL: {msg}")
        raise SystemExit(1)

    print("PASS: radius and uniformity checks")


if __name__ == "__main__":
    main()
