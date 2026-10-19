#ifndef SPHERE_SAMPLER_H
#define SPHERE_SAMPLER_H

#include <stddef.h>

/**
 * Uniform sampling of points on the surface of a sphere of radius R.
 *
 * Equal-area (correct) parameterization:
 *   u   ~ Uniform[-1, 1]   (z / R)
 *   phi ~ Uniform[0, 2 pi]
 *   x = R * sqrt(1 - u^2) * cos(phi)
 *   y = R * sqrt(1 - u^2) * sin(phi)
 *   z = R * u
 *
 * Naive polar sampling (biased toward the poles):
 *   theta ~ Uniform[0, pi]
 *   phi   ~ Uniform[0, 2 pi]
 *   x = R * sin(theta) * cos(phi)
 *   y = R * sin(theta) * sin(phi)
 *   z = R * cos(theta)
 */

typedef struct {
    double x;
    double y;
    double z;
} Point3D;

typedef enum {
    SAMPLE_EQUAL_AREA = 0,
    SAMPLE_NAIVE_THETA = 1
} SampleMethod;

typedef struct {
    Point3D *points;
    size_t count;
    double radius;
    SampleMethod method;
} PointCloud;

/**
 * Allocate and fill a point cloud with `count` samples on a sphere of
 * radius `radius` using `method`. The generator is seeded with `seed`
 * for reproducibility. Returns NULL on allocation failure or invalid args.
 */
PointCloud *sphere_sample(size_t count, double radius, long seed,
                          SampleMethod method);

/** Free a point cloud previously returned by sphere_sample. */
void point_cloud_free(PointCloud *cloud);

/**
 * Write points as whitespace-separated x y z rows.
 * Returns 0 on success, -1 on I/O error.
 */
int point_cloud_write(const PointCloud *cloud, const char *path);

#endif /* SPHERE_SAMPLER_H */
