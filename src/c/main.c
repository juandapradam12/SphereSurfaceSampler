#include "sphere_sampler.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    size_t count;
    double radius;
    long seed;
    const char *output;
    SampleMethod method;
} Config;

static void print_usage(const char *prog)
{
    fprintf(stderr,
            "Usage: %s [options]\n"
            "\n"
            "Random points on a sphere surface.\n"
            "\n"
            "Options:\n"
            "  -n, --count   N     Number of points (default: 5000)\n"
            "  -r, --radius  R     Sphere radius     (default: 1.0)\n"
            "  -s, --seed    S     RNG seed          (default: time-based)\n"
            "  -o, --output  PATH  Output .dat path  (default: results/points.dat)\n"
            "  -m, --method  NAME  equal-area | naive (default: equal-area)\n"
            "  -h, --help          Show this help\n",
            prog);
}

static int parse_method(const char *value, SampleMethod *method)
{
    if (strcmp(value, "equal-area") == 0 || strcmp(value, "uniform") == 0) {
        *method = SAMPLE_EQUAL_AREA;
        return 0;
    }
    if (strcmp(value, "naive") == 0 || strcmp(value, "naive-theta") == 0) {
        *method = SAMPLE_NAIVE_THETA;
        return 0;
    }
    return -1;
}

static const char *method_name(SampleMethod method)
{
    return method == SAMPLE_EQUAL_AREA ? "equal-area" : "naive";
}

static int parse_args(int argc, char **argv, Config *cfg)
{
    cfg->count = 5000;
    cfg->radius = 1.0;
    cfg->seed = (long)time(NULL);
    cfg->output = "results/points.dat";
    cfg->method = SAMPLE_EQUAL_AREA;

    for (int i = 1; i < argc; i++) {
        const char *arg = argv[i];
        const char *value = NULL;

        if (strcmp(arg, "-h") == 0 || strcmp(arg, "--help") == 0) {
            print_usage(argv[0]);
            exit(0);
        }

        if ((strcmp(arg, "-n") == 0 || strcmp(arg, "--count") == 0) ||
            (strcmp(arg, "-r") == 0 || strcmp(arg, "--radius") == 0) ||
            (strcmp(arg, "-s") == 0 || strcmp(arg, "--seed") == 0) ||
            (strcmp(arg, "-o") == 0 || strcmp(arg, "--output") == 0) ||
            (strcmp(arg, "-m") == 0 || strcmp(arg, "--method") == 0)) {
            if (i + 1 >= argc) {
                fprintf(stderr, "Missing value for %s\n", arg);
                return -1;
            }
            value = argv[++i];
        } else {
            fprintf(stderr, "Unknown argument: %s\n", arg);
            return -1;
        }

        if (strcmp(arg, "-n") == 0 || strcmp(arg, "--count") == 0) {
            char *end = NULL;
            long n = strtol(value, &end, 10);
            if (end == value || *end != '\0' || n <= 0) {
                fprintf(stderr, "Invalid count: %s\n", value);
                return -1;
            }
            cfg->count = (size_t)n;
        } else if (strcmp(arg, "-r") == 0 || strcmp(arg, "--radius") == 0) {
            char *end = NULL;
            double r = strtod(value, &end);
            if (end == value || *end != '\0' || r <= 0.0) {
                fprintf(stderr, "Invalid radius: %s\n", value);
                return -1;
            }
            cfg->radius = r;
        } else if (strcmp(arg, "-s") == 0 || strcmp(arg, "--seed") == 0) {
            char *end = NULL;
            long s = strtol(value, &end, 10);
            if (end == value || *end != '\0') {
                fprintf(stderr, "Invalid seed: %s\n", value);
                return -1;
            }
            cfg->seed = s;
        } else if (strcmp(arg, "-o") == 0 || strcmp(arg, "--output") == 0) {
            cfg->output = value;
        } else if (strcmp(arg, "-m") == 0 || strcmp(arg, "--method") == 0) {
            if (parse_method(value, &cfg->method) != 0) {
                fprintf(stderr, "Invalid method: %s (use equal-area|naive)\n",
                        value);
                return -1;
            }
        }
    }

    return 0;
}

int main(int argc, char **argv)
{
    Config cfg;
    if (parse_args(argc, argv, &cfg) != 0) {
        print_usage(argv[0]);
        return 1;
    }

    PointCloud *cloud =
        sphere_sample(cfg.count, cfg.radius, cfg.seed, cfg.method);
    if (cloud == NULL) {
        fprintf(stderr, "Failed to sample points (check count/radius/memory).\n");
        return 1;
    }

    if (point_cloud_write(cloud, cfg.output) != 0) {
        fprintf(stderr, "Failed to write output: %s\n", cfg.output);
        point_cloud_free(cloud);
        return 1;
    }

    printf("Wrote %zu points (R=%.6g, seed=%ld, method=%s) to %s\n",
           cloud->count, cloud->radius, cfg.seed, method_name(cloud->method),
           cfg.output);

    point_cloud_free(cloud);
    return 0;
}
