# Sampling methodology

## Problem

Generate $N$ independent samples that are **uniform with respect to surface
area** on a sphere of radius $R > 0$:

$$
S_R = \left\lbrace (x,y,z) \in \mathbb{R}^3 : x^2 + y^2 + z^2 = R^2 \right\rbrace.
$$

Naive sampling in spherical angles $(\theta,\phi)$ with $\theta$ drawn
uniformly from $[0,\pi]$ **does not** yield a uniform distribution on
$S_R$, because the ring area element scales with $\sin\theta$.

## Equal-area parameterization

A standard correction is to sample the cosine of the polar angle uniformly.
Let

$$
u \sim \mathcal{U}[-1, 1], \qquad
\phi \sim \mathcal{U}[0, 2\pi],
$$

independent, and set

$$
\begin{aligned}
x &= R\sqrt{1 - u^2}\,\cos\phi, \\
y &= R\sqrt{1 - u^2}\,\sin\phi, \\
z &= R\,u.
\end{aligned}
$$

Here $u = z/R = \cos\theta$. Because the surface measure on the unit sphere
satisfies

$$
\mathrm{d}A = \sin\theta\,\mathrm{d}\theta\,\mathrm{d}\phi
           = -\mathrm{d}(\cos\theta)\,\mathrm{d}\phi
           = -\mathrm{d}u\,\mathrm{d}\phi,
$$

drawing $u$ uniformly in $[-1,1]$ and $\phi$ uniformly in $[0,2\pi]$
produces the Haar (rotation-invariant) measure on $S_R$.

## Naive baseline (for contrast)

The CLI also exposes a deliberately biased method

$$
\theta \sim \mathcal{U}[0,\pi], \qquad \phi \sim \mathcal{U}[0,2\pi],
$$

mapped with the usual spherical-to-Cartesian transform. Under this law,
$u = \cos\theta$ has density

$$
f_u(u) = \frac{1}{\pi\sqrt{1-u^2}}, \qquad u \in (-1,1),
$$

so probability mass concentrates near the poles $u \to \pm 1$.

## Empirical checks

`validate_uniformity.py` reports:

1. **On-sphere geometry** — $\max_i \lvert \lVert p_i \rVert - R \rvert$ should be
   numerically tiny.
2. **Uniformity of $u=z/R$** — Pearson $\chi^2$ against
   $\mathcal{U}[-1,1]$ on a fixed binning. Equal-area samples stay near
   $\chi^2/\mathrm{dof} \approx 1$; naive samples inflate it sharply.

## Implementation notes

- The C library (`sphere_sample`) exposes both methods behind a small
  `PointCloud` API; the CLI selects them with `--method equal-area|naive`.
- A portable seeded RNG (SplitMix64-style) keeps clouds reproducible across
  platforms.
- Coordinates are whitespace-separated $x\; y\; z$ rows, then plotted and
  validated in Python.

## References

- Weisstein, E. W. “Sphere Point Picking.” *MathWorld*.
- Marsaglia, G. (1972). Choosing a point from the surface of a sphere.
  *Annals of Mathematical Statistics*, 43(2), 645–646.
