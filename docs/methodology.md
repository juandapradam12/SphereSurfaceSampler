# Sampling methodology

## Problem

Generate \(N\) independent samples that are **uniform with respect to surface
area** on a sphere of radius \(R > 0\):

$$
S_R = \bigl\{ (x,y,z) \in \mathbb{R}^3 : x^2 + y^2 + z^2 = R^2 \bigr\}.
$$

Naive sampling in spherical angles \((\theta,\phi)\) with \(\theta\) drawn
uniformly from \([0,\pi]\) **does not** yield a uniform distribution on
\(S_R\), because the ring area element scales with \(\sin\theta\).

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

Here \(u = z/R = \cos\theta\). Because the surface measure on the unit sphere
satisfies

$$
\mathrm{d}A = \sin\theta\,\mathrm{d}\theta\,\mathrm{d}\phi
           = -\mathrm{d}(\cos\theta)\,\mathrm{d}\phi
           = -\mathrm{d}u\,\mathrm{d}\phi,
$$

drawing \(u\) uniformly in \([-1,1]\) and \(\phi\) uniformly in \([0,2\pi]\)
produces the Haar (rotation-invariant) measure on \(S_R\).

## Implementation notes

- The C library (`sphere_sample`) exposes this construction behind a small
  `PointCloud` API; the CLI binary wraps it with a portable seeded RNG
  (SplitMix64-style) for reproducible clouds across platforms.
- Generated coordinates are written as whitespace-separated rows
  \(x\; y\; z\), then visualized with a 3D scatter plot.

## References

- Weisstein, E. W. “Sphere Point Picking.” *MathWorld*.
- Marsaglia, G. (1972). Choosing a point from the surface of a sphere.
  *Annals of Mathematical Statistics*, 43(2), 645–646.
