# Architecture

The repository separates **sampling**, **I/O**, and **visualization** so each
piece can evolve independently.

```
.
├── include/sphere_sampler.h   # Public C API
├── src/c/
│   ├── sphere_sampler.c       # Sampling + persistence
│   └── main.c                 # CLI entry point
├── src/python/
│   └── plot_sphere.py         # Visualization
├── examples/                  # Committed sample output
├── results/                   # Local generated artifacts (gitignored)
├── docs/                      # Use-case and method notes
└── Makefile                   # Build and pipeline targets
```

## Layers

| Layer | Responsibility |
|-------|----------------|
| **Core library** | Allocate a `PointCloud`, fill it with uniform sphere samples, free it, write it to disk. |
| **CLI** | Parse `-n/-r/-s/-o`, call the library, report status. No plotting logic. |
| **Visualization** | Load an \(N \times 3\) table and render a 3D scatter figure. |
| **Build** | `Makefile` compiles with C11 warnings enabled and orchestrates `sample` → `plot`. |

## Data contract

Point files are plain text: one point per line, three floating-point fields
separated by spaces. That keeps the C and Python sides loosely coupled and
easy to inspect or feed into other tools.
