#include "sphere_sampler.h"

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* SplitMix64-style generator: portable, seeded, no POSIX dependency. */
static uint64_t rng_state;

static void rng_seed(uint64_t seed)
{
    rng_state = seed;
    if (rng_state == 0) {
        rng_state = 0x9E3779B97F4A7C15ULL;
    }
}

static uint64_t rng_next_u64(void)
{
    uint64_t z = (rng_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static double rng_uniform01(void)
{
    /* Top 53 bits -> uniform in [0, 1). */
    return (rng_next_u64() >> 11) * (1.0 / 9007199254740992.0);
}

static double sample_u(void)
{
    return 2.0 * rng_uniform01() - 1.0;
}

static double sample_phi(void)
{
    return rng_uniform01() * (2.0 * M_PI);
}

static Point3D sample_on_sphere(double radius)
{
    const double u = sample_u();
    const double phi = sample_phi();
    const double rho = radius * sqrt(1.0 - u * u);

    Point3D p;
    p.x = rho * cos(phi);
    p.y = rho * sin(phi);
    p.z = radius * u;
    return p;
}

PointCloud *sphere_sample(size_t count, double radius, long seed)
{
    if (count == 0 || radius <= 0.0) {
        return NULL;
    }

    PointCloud *cloud = malloc(sizeof(*cloud));
    if (cloud == NULL) {
        return NULL;
    }

    cloud->points = malloc(count * sizeof(*cloud->points));
    if (cloud->points == NULL) {
        free(cloud);
        return NULL;
    }

    cloud->count = count;
    cloud->radius = radius;
    rng_seed((uint64_t)seed);

    for (size_t i = 0; i < count; i++) {
        cloud->points[i] = sample_on_sphere(radius);
    }

    return cloud;
}

void point_cloud_free(PointCloud *cloud)
{
    if (cloud == NULL) {
        return;
    }
    free(cloud->points);
    free(cloud);
}

int point_cloud_write(const PointCloud *cloud, const char *path)
{
    if (cloud == NULL || path == NULL) {
        return -1;
    }

    FILE *out = fopen(path, "w");
    if (out == NULL) {
        return -1;
    }

    for (size_t i = 0; i < cloud->count; i++) {
        const Point3D *p = &cloud->points[i];
        if (fprintf(out, "%.10f %.10f %.10f\n", p->x, p->y, p->z) < 0) {
            fclose(out);
            return -1;
        }
    }

    if (fclose(out) != 0) {
        return -1;
    }
    return 0;
}
