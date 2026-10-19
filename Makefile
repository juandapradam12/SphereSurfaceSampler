CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -Wpedantic -O2
CPPFLAGS = -Iinclude
LDFLAGS  =
LDLIBS   = -lm

BIN_DIR  = bin
SRC_DIR  = src/c
RESULTS  = results
EXAMPLES = examples

SAMPLER  = $(BIN_DIR)/sphere_sampler
OBJS     = $(BIN_DIR)/sphere_sampler.o $(BIN_DIR)/main.o

N        ?= 5000
R        ?= 1.0
SEED     ?= 42
POINTS   ?= $(RESULTS)/points.dat
FIGURE   ?= $(RESULTS)/sphere.png
POINTS_NAIVE ?= $(RESULTS)/points_naive.dat

.PHONY: all sample plot gif validate run test example clean help

all: $(SAMPLER)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(RESULTS):
	mkdir -p $(RESULTS)

$(BIN_DIR)/%.o: $(SRC_DIR)/%.c include/sphere_sampler.h | $(BIN_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(SAMPLER): $(OBJS)
	$(CC) $(LDFLAGS) $^ -o $@ $(LDLIBS)

sample: $(SAMPLER) | $(RESULTS)
	$(SAMPLER) -n $(N) -r $(R) -s $(SEED) -m equal-area -o $(POINTS)
	$(SAMPLER) -n $(N) -r $(R) -s $(SEED) -m naive -o $(POINTS_NAIVE)

plot: $(POINTS)
	python3 src/python/plot_sphere.py -i $(POINTS) -o $(FIGURE)

gif: $(POINTS)
	python3 src/python/animate_sphere.py -i $(POINTS) -o $(RESULTS)/sphere.gif

validate: $(POINTS) $(POINTS_NAIVE)
	python3 src/python/validate_uniformity.py \
		--equal-area $(POINTS) \
		--naive $(POINTS_NAIVE) \
		--radius $(R) \
		--figure $(RESULTS)/uniformity.png \
		--report $(RESULTS)/uniformity.json

run: sample plot validate

test: $(SAMPLER) | $(RESULTS)
	$(SAMPLER) -n 3000 -r 1.25 -s 7 -m equal-area -o $(RESULTS)/test_eq.dat
	$(SAMPLER) -n 3000 -r 1.25 -s 7 -m naive -o $(RESULTS)/test_naive.dat
	python3 src/python/validate_uniformity.py \
		--equal-area $(RESULTS)/test_eq.dat \
		--naive $(RESULTS)/test_naive.dat \
		--radius 1.25 \
		--figure $(RESULTS)/test_uniformity.png \
		--report $(RESULTS)/test_uniformity.json
	@echo "All smoke checks passed."

example: $(SAMPLER) | $(EXAMPLES)
	$(SAMPLER) -n 5000 -r 1.0 -s 42 -m equal-area -o $(EXAMPLES)/points.dat
	$(SAMPLER) -n 5000 -r 1.0 -s 42 -m naive -o $(EXAMPLES)/points_naive.dat
	python3 src/python/plot_sphere.py \
		-i $(EXAMPLES)/points.dat \
		-o $(EXAMPLES)/sphere.png \
		--title "Equal-area samples on the unit sphere (N=5000)"
	python3 src/python/animate_sphere.py \
		-i $(EXAMPLES)/points.dat \
		-o $(EXAMPLES)/sphere.gif \
		--title "Equal-area samples (rotating view)"
	python3 src/python/plot_sphere.py \
		-i $(EXAMPLES)/points_naive.dat \
		-o $(EXAMPLES)/sphere_naive.png \
		--title "Naive θ samples on the unit sphere (N=5000)"
	python3 src/python/validate_uniformity.py \
		--equal-area $(EXAMPLES)/points.dat \
		--naive $(EXAMPLES)/points_naive.dat \
		--radius 1.0 \
		--figure $(EXAMPLES)/uniformity.png \
		--report $(EXAMPLES)/uniformity.json

clean:
	rm -rf $(BIN_DIR) \
		$(RESULTS)/points.dat $(RESULTS)/points_naive.dat \
		$(RESULTS)/sphere.png $(RESULTS)/sphere.gif $(RESULTS)/uniformity.png \
		$(RESULTS)/uniformity.json \
		$(RESULTS)/test_eq.dat $(RESULTS)/test_naive.dat \
		$(RESULTS)/test_uniformity.png $(RESULTS)/test_uniformity.json

help:
	@echo "Targets:"
	@echo "  all       Build the C sampler binary"
	@echo "  sample    Generate equal-area and naive point clouds"
	@echo "  plot      Render 3D scatter from equal-area samples"
	@echo "  gif       Rotating GIF of equal-area samples"
	@echo "  validate  Radius + u=z/R uniformity checks and figure"
	@echo "  run       sample + plot + validate"
	@echo "  test      Smoke test (build + statistical checks)"
	@echo "  example   Refresh committed examples/"
	@echo "  clean     Remove build artifacts and generated results"
