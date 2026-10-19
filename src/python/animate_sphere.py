#!/usr/bin/env python3
"""Render a rotating GIF of a sphere-surface point cloud."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def load_points(path: Path, max_points: int | None) -> np.ndarray:
    points = np.loadtxt(path)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected N x 3 point file, got shape {points.shape}")
    if max_points is not None and len(points) > max_points:
        rng = np.random.default_rng(0)
        idx = rng.choice(len(points), size=max_points, replace=False)
        points = points[idx]
    return points


def animate_sphere(
    points: np.ndarray,
    output: Path,
    title: str | None = None,
    frames: int = 36,
    fps: int = 12,
    elev: float = 22.0,
) -> None:
    radius = float(np.max(np.linalg.norm(points, axis=1)))
    limit = max(radius * 1.15, 1.0)

    fig = plt.figure(figsize=(5.2, 4.8), dpi=90)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(title or f"Equal-area samples (N={len(points)})")

    ax.scatter(
        points[:, 0],
        points[:, 1],
        points[:, 2],
        s=3,
        c=points[:, 2],
        cmap="viridis",
        depthshade=True,
        linewidths=0,
        alpha=0.85,
    )

    def update(frame: int):
        ax.view_init(elev=elev, azim=(360.0 * frame) / frames)
        return ()

    output.parent.mkdir(parents=True, exist_ok=True)
    anim = animation.FuncAnimation(
        fig, update, frames=frames, interval=1000 / fps, blit=False
    )
    anim.save(output, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a rotating GIF of sphere surface samples."
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
        default=Path("results/sphere.gif"),
        help="Output GIF path",
    )
    parser.add_argument("--title", default=None, help="Optional plot title")
    parser.add_argument("--frames", type=int, default=36, help="Frames per revolution")
    parser.add_argument("--fps", type=int, default=12, help="GIF frames per second")
    parser.add_argument(
        "--max-points",
        type=int,
        default=2500,
        help="Subsample size for a lighter GIF (0 = use all)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    max_points = None if args.max_points <= 0 else args.max_points
    points = load_points(args.input, max_points=max_points)
    animate_sphere(
        points,
        args.output,
        title=args.title,
        frames=args.frames,
        fps=args.fps,
    )
    size_kb = args.output.stat().st_size / 1024
    print(f"Saved GIF to {args.output} ({size_kb:.0f} KiB, N={len(points)})")


if __name__ == "__main__":
    main()
