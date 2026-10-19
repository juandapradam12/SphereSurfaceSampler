#!/usr/bin/env python3
"""Visualize a point cloud sampled on a sphere surface."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # registers 3D projection


def load_points(path: Path) -> np.ndarray:
    points = np.loadtxt(path)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected N x 3 point file, got shape {points.shape}")
    return points


def plot_sphere(
    points: np.ndarray,
    output: Path,
    title: str | None = None,
    show: bool = False,
) -> None:
    radius = float(np.max(np.linalg.norm(points, axis=1)))
    limit = max(radius * 1.15, 1.0)

    fig = plt.figure(figsize=(8, 7), dpi=120)
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(
        points[:, 0],
        points[:, 1],
        points[:, 2],
        s=4,
        c=points[:, 2],
        cmap="viridis",
        depthshade=True,
        linewidths=0,
        alpha=0.85,
    )

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(title or f"Uniform sphere samples (N={len(points)}, R≈{radius:.3g})")

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot 3D scatter of points sampled on a sphere."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("results/points.dat"),
        help="Input whitespace-separated x y z file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("results/sphere.png"),
        help="Output image path",
    )
    parser.add_argument("--show", action="store_true", help="Display the figure")
    parser.add_argument("--title", default=None, help="Optional plot title")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    points = load_points(args.input)
    plot_sphere(points, args.output, title=args.title, show=args.show)
    print(f"Saved figure to {args.output}")


if __name__ == "__main__":
    main()
