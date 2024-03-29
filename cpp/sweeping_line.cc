// SPDX-License-Identifier: Apache-2.0
// Copyright 2023: Amazon Web Services, Inc

// This code reads a unit-disk graph in METIS format and
// computes the number of ground states and first excited
// states for the Maximum Independent Set problem on this
// graph.
//
// Notes:
//
//   * The METIS 4 format is described on page 3, section 3.1 of
//     http://algo2.iti.kit.edu/schulz/software_releases/kamis.pdf
//
//   * The algorithm is built on a sweeping-line paradigm, keeping
//     track of a full enumaration of states on this moving boundary
//     (but summarizing for nodes previously visited that are not
//      connected to new nodes, and, therefore, have no impact on
//      upcoming node independence considerations).
//
//   * This solver is NOT a generic solution for arbitrary graphs.
//     The underlying algorithm is able to produce a solution to
//     graphs up to LxL ~= 30x30 because the restriction to unit
//     dist graphs makes the graph quasi-planar.
//
//   * Runtime is exponential in the width of the graph (i.e, `L`),
//     because the number of potential boundary assignments grows
//     exponentially with the number of nodes on the boundary
//     (and the code tracks all boundary realizations while sweeping)
//
// Usage:
//
//   make sweeping_line
//   ./sweeping_line your_metis_instance.txt
//
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

// Renaming the types we will use for readability.
using Cost = uint16_t;
using NodeId = uint16_t;
using Key = uint64_t;
using Count = double;

// Helper function to read lines from a file
vector<string> get_lines(string filename) {
  vector<string> lines;
  ifstream input(filename);
  string line;
  while (getline(input, line)) {
    lines.push_back(line);
  }
  return lines;
}

// Helper function to split a string into numbers
vector<uint16_t> get_numbers(const string &line) {
  vector<uint16_t> numbers;
  string delim = " \t";
  size_t a = line.find_first_not_of(delim);
  size_t b = line.find_first_of(delim, a);
  while (a < b) {
    int number = stoi(line.substr(a, b - a));
    numbers.push_back(number);
    a = line.find_first_not_of(delim, b);
    b = line.find_first_of(delim, a);
  }
  return numbers;
}

// Representation of a Union-Disk MIS instance
class Instance {
public:
  Instance() : L(0), N(0) {}

  // Load instances from a metis4 txt file
  void load(string filename) {
    auto lines = get_lines(filename);
    uint16_t data_line = 0;
    for (size_t i = 0; i < lines.size(); i++) {
      const auto &line = lines[i];
      if (line.size() == 0)
        continue; // ignore empty lines
      if (line[0] == '%') {
        // Check for L=? in comment lines. (It's not used explicitly in the
        // computation but, this is a safeguard against feeding files not
        // generated by us -- and thus potentially not ordered as this counter
        // assumes).
        if (line.substr(0, 5) == "%% L=") {
          L = stoi(line.substr(5));
          cout << "found L=" << L << endl;
        }
        continue; // ignore comment lines.
      }
      auto entries = get_numbers(line);
      if (data_line == 0) {
        // first data line defines the graph size
        N = entries[0];
        if (entries.size() == 3) {
          assert(entries[2] == 0);
        }
        adj.resize(1); // sentinel to make indices 1-indexed.
      } else {
        // store adjacency list
        adj.push_back(entries);
      }
      data_line++;
    }
  }

  // The number of lines/columns in the Union Jack lattice
  // TODO(randrist): Consider whether we want to generalize this
  // to WxH (i.e., different dimensions for width, height).
  int L;
  // The number of nodes in the graph
  int N;
  // Adjacency list representation of the graph
  // NOTE: indices of the outer vector are 1-based (as they are in the metis
  // format). The first entry of the outer vector is therefore an empty list
  // (since 0 is not a NodeId in this representation).
  vector<vector<uint16_t>> adj;
};

// Representation of a single variant
//
// Does not contain the actual mis assignment, as this is
// stored within the key in Variants. We are keeping track of
// the best cost achieved and how many ways to achieve it for
// this boundary. The logic assumes that the first excited
// state is always off by 1 (which I believe is guaranteed,
// since you can create a 1E by dropping any node from a GS)
class Variant {
public:
  Variant() : cost(0), count(0) {}

  // Logic to update the counts when a new variant is recorded
  //
  // If the new cost is better, we need to shuffle things
  // around a bit (depending on whether is +1 or more).
  void record(Cost cost, Count count, Count count2) {
    if (cost > this->cost + 1) {
      // We found a 2+ better MIS, drop all previous counts.
      this->cost = cost;
      this->count = count;
      this->count2 = count2;
    } else if (cost == this->cost + 1) {
      // We found a 1 better MIS, move best count to count2
      this->cost = cost;
      this->count2 = this->count + count2;
      this->count = count;
    } else if (cost == this->cost) {
      // We equalized the previous best, just add counts
      this->count += count;
      this->count2 += count2;
    } else if (cost == this->cost - 1) {
      // We are recording a count for the 1st excited.
      this->count2 += count;
    }
  }

  Cost cost;    // Best MIS size attained for this boundary variant
  Count count;  // How many ways this best size can be obtained
  Count count2; // How many times we can get a 1-smaller MIS
};

// Representation of all the variants for a given boundary
class Variants {
public:
  Variants() : variants(nullptr) {
    variants = new unordered_map<Key, Variant>();
  }

  ~Variants() {
    delete variants;
    variants = nullptr;
  }

  // Add a variant to this set (or add to it, if it exists).
  void add_variant(const Key &key, Cost cost, Count count, Count count2) {
    if (variants->find(key) == variants->end()) {
      (*variants)[key] = Variant();
    }
    (*variants)[key].record(cost, count, count2);
  }

  // Clear all variants.
  void clear() { variants->clear(); }

  // Swap all variants with another set (o(1)).
  void swap(Variants &other) { std::swap(variants, other.variants); }

  // Store the variants in a hash map.
  unordered_map<Key, Variant> *variants;
};

// Find the boundaries assuming we are processing the nodes 1..N
//
// The boundary is the set of nodes that have been processed but are
// still connected to at least 1 unprocessed node. We need to track
// its state in the variant set because it still affects potential
// assignment of that upcoming unprocessed node.
//
// We calculate boundaries[i] as the distance between the first node
// in the boundary to the last one (inclusive; in the ordering the
// nodes are specified in the input).
vector<NodeId> find_boundaries(const Instance &instance) {
  // The boundary sizes we want to compute
  vector<NodeId> boundaries(instance.N + 1);
  // The number of processed neighbors of each node. Once this number
  // grows to the size of the adjacency list of a node, it can be
  // dropped from the boundary.
  vector<NodeId> processed_neighbors(instance.N + 1);
  // Keep track of the earliest node in the boundary
  // (increased as nodes have all their neighbors processed)
  NodeId first_active = 1;
  for (NodeId i = 1; i < instance.N; i++) {
    // We are processing node i
    for (NodeId j : instance.adj[i]) {
      // Increased the counter of all neighbors of i
      processed_neighbors[j]++;
    }
    // Update the earliest node that is still in the boundary
    // TODO(randrist): Check that this handles non-single-component graphs
    // correctly.
    for (NodeId j = first_active; j <= i; j++) {
      if (processed_neighbors[j] < instance.adj[j].size()) {
        break;
      }
      first_active = j + 1;
    }
    // Record the boundary for i. This is inclusive (i.e. |2..4| = 3).
    boundaries[i] = i - first_active + 1;
  }
  return boundaries;
}

// Method to count the number of ground states and first excited states
// of an instance.
void count_ground_states(const Instance &instance) {
  // Determine the size of the boundary at each step
  //
  // NOTE: This assumes nodes are given in a sensible order
  // such that the boundary does not grow too large. This is
  // the case for MIS on Union-Jack (i.e., the graphs obtained
  // from unit circle MIS) when nodes are ordered according
  // to the 2D representation.
  vector<NodeId> boundaries = find_boundaries(instance);

  // The code can handle boundary sizes up to 64 nodes.
  // Check that the boundary is never bigger than that.
  for (NodeId i = 1; i < instance.N; i++) {
    if (boundaries[i] > 64) {
      cout << "[ERR] Boundary at step " << i << " is " << boundaries[i]
           << " > 64." << endl;
      cout << "Please check that nodes are sorted in the input!";
      exit(0);
    }
  }

  // Keep track of the variants at the previous and next boundary at each step
  Variants prev, next;
  // Initialize the first boundary (no nodes processed) as
  // 0 -- no prior assignments
  // 0 -- best mis size = 0
  // 1 -- 1 way to achieve this
  // 0 -- no first excided states
  prev.add_variant(0, 0, 1, 0);
  for (uint16_t i = 1; i <= instance.N; i++) {
    // Clear the variants in the next set
    // (might be populated because we are swapping at the end of this loop)
    next.clear();

    // Limit bits in the new key to the new boundary
    //
    // this drops information that is no longer relevant because those nodes
    // no longer have any connection to the unprocessed portion of the graph
    // (i.e., they are no longer part of the "active boundary").
    // The result is that variant counting is summarized w.r.t. to these nodes
    // and the list of variants tracked is limited to 2^{boundary size}.
    Key clip = (Key(1) << (boundaries[i])) - 1;

    // Compute which bits are relevant in the previous key (neighbors of i)
    //
    // This precomputes the check we need to perform on the boundary tGo know
    // whether we can add node i to the MIS in a specific variant. The mask
    // represents all the nodes on the boundary which are connected to node i.
    Key mask = 0;
    for (const auto &j : instance.adj[i]) {
      if (j < i) {
        mask = mask | (Key(1) << (i - j - 1));
      }
    }

    // Generate variants in the next variant set from the ones in prev
    for (const auto &entry : *prev.variants) {
      // unpack previous variant (for readability)
      auto key = entry.first;
      const auto &variant = entry.second;

      // The new key is the previous one shifted and clipped:
      // the shift makes room for node i and the clip drops old nodes
      // NOTE: shift adds a zero in the least significant bit, so new_key
      // represents the new variant where node i is *NOT* in the MIS.
      uint64_t new_key = (key << 1) & clip;

      // Record the variant where we don't add node i to the MIS
      next.add_variant(new_key, variant.cost, variant.count, variant.count2);

      // If node i can be added to the MIS (i.e., not connected to any
      // included nodes in the boundary of the current variant), also add
      // a variant where node i is added to the MIS.
      if ((key & mask) == 0) {
        // NOTE: We are adding one to the new_key, which sets the node i bit
        next.add_variant(new_key + 1, variant.cost + 1, variant.count,
                         variant.count2);
      }
    }

    // Move the variants in next to prev for the next step (to avoid copy)
    prev.swap(next);
  }

  // Look at all the boundary realizations after processing the last node and
  // add up the ones which represent ground states and first excited states.
  Variant best;
  for (const auto &entry : *prev.variants) {
    const auto &variant = entry.second;
    best.record(variant.cost, variant.count, variant.count2);
  }

  // Print the result.
  cout << "|MSI| #GS #1E" << endl;
  cout << best.cost << " " << double(best.count) << " " << double(best.count2)
       << endl;
};

int main(int argc, char **argv) {
  Instance instance;
  if (argc != 2) {
    cout << "Usage: " << argv[0] << " [INSTANCE.txt]";
    exit(EXIT_FAILURE);
  }
  instance.load(argv[1]);
  if (instance.L == 0) {
    cout << "[WARN] Did not find \"% L = ?\" in the file." << endl;
    cout << "Make sure to use a metis4 format txt instance file." << endl;
  }
  if (instance.L > 63) {
    // Kind of pointless, this code is prohibitively slow well before that.
    cout << "[ERR] Found instance bigger than L=63." << endl;
    cout << "This code cannot handle L>63." << endl;
    exit(EXIT_FAILURE);
  }
  count_ground_states(instance);
  return EXIT_SUCCESS;
}
