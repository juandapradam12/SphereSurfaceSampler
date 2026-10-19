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

.PHONY: all sample plot run clean example help

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
	$(SAMPLER) -n $(N) -r $(R) -s $(SEED) -o $(POINTS)

plot: $(POINTS)
	python3 src/python/plot_sphere.py -i $(POINTS) -o $(FIGURE)

run: sample plot

example: $(SAMPLER) | $(EXAMPLES)
	$(SAMPLER) -n 5000 -r 1.0 -s 42 -o $(EXAMPLES)/points.dat
	python3 src/python/plot_sphere.py \
		-i $(EXAMPLES)/points.dat \
		-o $(EXAMPLES)/sphere.png \
		--title "Uniform samples on the unit sphere (N=5000)"

clean:
	rm -rf $(BIN_DIR) $(RESULTS)/points.dat $(RESULTS)/sphere.png

help:
	@echo "Targets:"
	@echo "  all      Build the C sampler binary"
	@echo "  sample   Generate point cloud (N=$(N), R=$(R), SEED=$(SEED))"
	@echo "  plot     Render 3D scatter from $(POINTS)"
	@echo "  run      sample + plot"
	@echo "  example  Refresh committed example under examples/"
	@echo "  clean    Remove build artifacts and generated results"
