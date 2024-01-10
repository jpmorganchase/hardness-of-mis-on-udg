// SPDX-License-Identifier: Apache-2.0
// Copyright 2023: Amazon Web Services, Inc
//
// This file implement simulated annealing with a geometric schedule.
#pragma once

#include <iostream>

#include "markov_chain.h"
#include "random.h"

class SimulatedAnnealing {
public:
  // Create an uninitialized simulated annealing instance.
  SimulatedAnnealing()
      : beta_min(1.0), beta_max(1.0), seed(0), model(nullptr),
        target_cost(0.0) {}

  // Setters
  void set_model(const IndependentSet *model) { this->model = model; }
  void set_seed(int seed) { rng.seed(seed); }
  void set_target_cost(double target_cost) { this->target_cost = target_cost; }
  void set_betas(double beta_min, double beta_max) {
    this->beta_min = beta_min;
    this->beta_max = beta_max;
  }

  double beta_min, beta_max, target_cost;
  uint64_t seed;
  const IndependentSet *model;

  void run(int replicas, int steps) {
    // Runtime statistics
    int groundstate = 0;          // how many times we found the ground state
    double acceptance_rate = 0.0; // the average acceptance rate

    for (int k = 0; k < replicas; k++) {
      Rng r;
      r.seed(rng.uint32());
      MarkovChain chain;
      chain.set_model(model);
      chain.set_rng(&r);
      chain.init();
      int step = 0;
      double progress = 0;
      bool groundstate_found = false;
      for (step = 0; step < steps; step++) {
        if (steps > 1)
          progress = (step % steps) / double(steps - 1);
        double beta = beta_min * pow(beta_max / beta_min, progress);
        chain.set_beta(beta);
        double before = chain.best_cost;
        chain.make_sweep();
        if (chain.best_cost == target_cost) {
          groundstate_found = true;
          // Intentionally NOT breaking here to calculate average runtime
          // of a replica from the total duration.
          // break;
        }
      }

      if (groundstate_found)
        groundstate++;
      acceptance_rate += chain.n_accepted / double(chain.n_moves);
    }
    std::cout << "# N steps b_min b_max replicas gs acc" << std::endl;
    std::cout << model->N << " " << steps << " " << beta_min << " " << beta_max
              << " " << replicas << " " << groundstate << " "
              << acceptance_rate / replicas << std::endl;
  }

  Rng rng;
};
