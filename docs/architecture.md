# Architecture

The repository separates **sampling**, **I/O**, **visualization**, and
**validation** so each piece can evolve independently.

```
.
├── include/sphere_sampler.h      # Public C API
├── src/c/
│   ├── sphere_sampler.c          # Sampling + persistence
│   └── main.c                    # CLI entry point
├── src/python/
│   ├── plot_sphere.py            # 3D visualization
│   ├── animate_sphere.py         # Rotating GIF
│   └── validate_uniformity.py    # Radius + u=z/R checks
├── examples/                     # Committed sample output
├── results/                      # Local generated artifacts (gitignored)
├── docs/                         # Use-case and method notes
├── .github/workflows/ci.yml      # Build + smoke test
└── Makefile                      # Build and pipeline targets
```

## Layers

| Layer | Responsibility |
|-------|----------------|
| **Core library** | Allocate a `PointCloud`, fill it (`equal-area` or `naive`), free it, write it to disk. |
| **CLI** | Parse `-n/-r/-s/-o/-m`, call the library, report status. |
| **Visualization** | Load an $N \times 3$ table and render a 3D scatter figure. |
| **Validation** | Check on-sphere radii and $\chi^2$ uniformity of $u=z/R$; optional naive contrast plot. |
| **Build / CI** | `Makefile` orchestrates `sample` → `plot` → `validate`; GitHub Actions runs `make test`. |

## Data contract

Point files are plain text: one point per line, three floating-point fields
separated by spaces. That keeps the C and Python sides loosely coupled and
easy to inspect or feed into other tools.
