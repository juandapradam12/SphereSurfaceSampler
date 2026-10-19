# Uniform Point Sampling on a Sphere

A small scientific-computing use case: generate a **uniform random distribution
of points on the surface of a sphere** of arbitrary radius \(R\), visualize the
cloud, and **validate** the surface measure against a naive baseline.

This repository modernizes an early coursework prototype into a portfolio-ready
example with a clear C library boundary, a thin CLI, Python plotting/validation,
and documented methodology.

<p align="center">
  <img src="examples/sphere.png" alt="Uniform samples on the unit sphere" width="520"/>
</p>

<p align="center">
  <img src="examples/uniformity.png" alt="Equal-area vs naive u=z/R histograms" width="720"/>
</p>

## Why this matters

Uniform sphere sampling shows up in Monte Carlo integration, directional
statistics, molecular / condensed-matter models, and graphics (environment
maps, particle systems). Getting the measure right matters: sampling polar
angle \(\theta\) uniformly produces clustering at the poles; sampling
\(u = \cos\theta\) uniformly does not.

## Method (short)

Draw independent uniforms

$$
u \sim \mathcal{U}[-1,1], \qquad \phi \sim \mathcal{U}[0, 2\pi]
$$

and map them to Cartesian coordinates on the sphere of radius \(R\):

$$
\begin{aligned}
x &= R\sqrt{1-u^{2}}\,\cos\phi,\\
y &= R\sqrt{1-u^{2}}\,\sin\phi,\\
z &= R\,u.
\end{aligned}
$$

The naive baseline draws \(\theta \sim \mathcal{U}[0,\pi]\) instead; then
\(u=\cos\theta\) follows density \(1/(\pi\sqrt{1-u^2})\) and piles up at the
poles. Empirical checks use on-sphere radius error and a \(\chi^2\) test of
\(u=z/R\) against \(\mathcal{U}[-1,1]\).

Full derivation: [docs/methodology.md](docs/methodology.md).  
Layout and layering: [docs/architecture.md](docs/architecture.md).

## Project layout

```
include/sphere_sampler.h          Public C API (PointCloud)
src/c/                            Sampler library + CLI
src/python/plot_sphere.py         3D visualization
src/python/validate_uniformity.py Radius + uniformity checks
examples/                         Sample data, sphere + uniformity figures
docs/                             Methodology and architecture
.github/workflows/ci.yml          Build + smoke test
```

## Requirements

- C compiler with C11 support (`cc` / `gcc` / `clang`)
- `make`
- Python 3.10+
- `numpy`, `matplotlib` (see `requirements.txt`)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick start

```bash
make run                 # sample (both methods) + plot + validate
# or with overrides:
make run N=8000 R=2.5 SEED=7
make test                # smoke checks used by CI
```

Outputs land in `results/` (`points.dat`, `points_naive.dat`, `sphere.png`,
`uniformity.png`, `uniformity.json`).  
Refresh the committed demo under `examples/` with `make example`.

### CLI

```bash
make
./bin/sphere_sampler --help
./bin/sphere_sampler -n 5000 -r 1.0 -s 42 -m equal-area -o results/points.dat
./bin/sphere_sampler -n 5000 -r 1.0 -s 42 -m naive -o results/points_naive.dat
python3 src/python/plot_sphere.py -i results/points.dat -o results/sphere.png
python3 src/python/validate_uniformity.py \
  --equal-area results/points.dat \
  --naive results/points_naive.dat \
  --radius 1.0
```

## Design choices

- **Library vs. driver**: sampling lives in `sphere_sampler.c`; `main.c` only
  handles arguments and exit codes.
- **Two methods, one API**: `equal-area` (correct) and `naive` (biased) share
  the same `PointCloud` path for fair comparison.
- **Reproducibility**: optional RNG seed (`-s`) for deterministic clouds.
- **Evidence, not only plots**: validation asserts radius fidelity and
  \(\chi^2/\mathrm{dof}\) for \(u=z/R\).
- **Loose coupling**: whitespace \(x\,y\,z\) files are the handoff between C
  and Python—no shared runtime.
- **Explicit artifacts**: generated results are gitignored; `examples/` keeps
  stable visuals for the README.

## License

MIT — see [LICENSE](LICENSE).
