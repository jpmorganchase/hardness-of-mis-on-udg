###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
"""generator.py: Generator for unweighted MIS instances on Union Jack lattices."""

__author__ = "Ruben S. Andrist"
__email__ = "randrist@amazon.com"
__version__ = "0.2"

import random
import math
from instance import Instance
from typing import Optional, List

from utils import format_radius


class Generator:
    """Genereator for unweighted MIS instances on Union Jack lattices.

    This generator produces an L*L lattice of occupied/vacant sites and returns
    the resulting graph (assuming union jack connections) as an MIS instance.

    NOTE: A single component is guaranteed when the random sites are selected.
    """

    def __init__(self, L: int, density: float = 0.8, r: float = 2 ** 0.5) -> None:
        """Create a generator for a fixed lattice size and density.

        Args:
          L (int): lattice size, 0 < L < 50
          density (float): density, 0 < density < 1.0
          r (float): radius of interaction, two nodes are connected if within distance r, 1 <= r < 10

        NOTE: The density must be chosen such that N = round(L*L*density) > 1
        The precision on r is 0.001, for r<=250 the minimum distance difference is 0.002.
        """
        assert 0 < L and L < 52
        assert 1 <= r and r < 10
        assert round(density * L * L) > 1 and density <= 1.0
        self.L = L
        self.density = density
        self.r = format_radius(r)
        self.directions = self.generate_all_directions(r)
        self.seed = None
        self.rng = None

    @staticmethod
    def generate_all_directions(r):
        """
        Generate directions to grid points with the disk of radius r using brute force
        """
        directions = []
        for x in range(-math.floor(r), math.floor(r) + 1):
            for y in range(-math.floor(r), math.floor(r) + 1):
                if 0 < x ** 2 + y ** 2 <= r ** 2:
                    directions.append((x, y))
        return directions

    def generate(self, seed: Optional[int] = None, verbose: bool = False) -> Instance:
        """Generate an MIS instance on a Union Jack Lattice.

        This returns a random MIS instance as an `Instance`, which can then be
        rendered in various formats.

        Args:
          seed (int): Seed for the random number generator (optional)
          verbose (bool): Print as ascii while generating (default: False)

        Returns:
          Instance: The generated instance

        NOTE: If no seed is provided, a random one in 0..100000 is used.
        """
        # Set or choose the seed.
        if seed is None:
            seed = random.randrange(100000)
        self.seed = seed
        self.rng = random.Random(seed)

        # Generate the lattice representation
        grid = self.generate_grid()
        if verbose:
            self.print_ascii(grid)

        # Build the instance
        instance = Instance(
            L=self.L,
            density=self.density,
            seed=self.seed,
            r=self.r,
            version=__version__,
        )

        # Populate the edges in the instance from the grid
        for x in range(self.L):
            for y in range(self.L):
                if grid[x][y] is None:
                    continue
                center = grid[x][y]
                instance.add_node(id_nb=center, x=x, y=y)
                for delta_x, delta_y in self.directions:
                    x_bis = x + delta_x
                    y_bis = y + delta_y
                    if 0 <= x_bis < self.L and 0 <= y_bis < self.L:
                        next_neighbour = grid[x_bis][y_bis]
                        if next_neighbour is not None:
                            instance.add_edge(next_neighbour, center)
        return instance

    # Lattice representation (with sentinel row/column).
    # Each entry in the (L+1)*(L+1) array is either None or a
    # unique id in 0..round(L*L*density).
    Grid = List[List[Optional[int]]]

    def generate_grid(self) -> Grid:
        """Create a 2d grid with occupied and vacant sites.

        This removes nodes until exactly round(N * density) nodes remain.
        Nodes randomly proposed for removal are only removed if doing so
        does not split the graph into multiple components.

        Returns an (L+1)*(L+1) grid with each site either None=vacant or
        a unique id 0..round(N * density).

        NOTE: A column and row of all None are added on the right and at the
        bottom as sentinels. This simplifies checks whether neighbors are
        occupied (because [x+1] and [x-1] will access these for x = {0,L-1}).
        """
        # Build the initial (fully populated) grid.
        grid = [[] for _ in range(self.L)]
        for i in range(self.L):
            grid[i] = [1] * self.L

        # Choose the random order in which to attempt to remove nodes
        sites = []
        for i in range(self.L):
            for j in range(self.L):
                sites += [(i, j)]
        self.rng.shuffle(sites)

        # Keep track of nodes still populated
        N = len(sites)
        occupied = N
        target = round(N * self.density)

        # Remove nodes in the preshuffled order
        # NOTE: this does multiple rounds if target is not attained during the
        # first round due to unremovable nodes. This very rarely happens for
        # d=0.8, but for lower densities it could introduce some bias when it
        # does.
        i = 0
        while occupied > target:
            x, y = sites[i]
            if grid[x][y] != 0 and self.can_remove(grid, x, y):
                grid[x][y] = 0
                occupied -= 1
            i = (i + 1) % N

        # transform grid from {0,1} to {id | None}
        n = 0
        for x in range(self.L):
            for y in range(self.L):
                if grid[x][y] == 0:
                    grid[x][y] = None
                else:
                    grid[x][y] = n
                    n += 1
            # add sentinel col on the right
            grid[x] += [None]
        # add sentinel row at the bottom
        grid += [[None] * (self.L + 1)]

        return grid

    def can_remove(self, grid: Grid, x: int, y: int) -> bool:
        """Check whether a site can be removed.

        Expects grid to be an L*L lattice of 0=vacant, 1=occupied

        This check prohibits removal of a node if doing so would split the
        resulting graph into multiple components. The main motivation for
        doing this is that some output formats (i.e., KaMIS) do NOT support
        unconnected single nodes.

        In practice this happens rarely for d=0.8, but it does have an effect
        at lower densities.
        """
        # movement directions
        dirs = self.directions

        # identify neighbors of the node (x,y)
        neighbors = []
        for d in dirs:
            u, v = x + d[0], y + d[1]
            if u < 0 or u >= self.L:
                continue
            if v < 0 or v >= self.L:
                continue
            if grid[u][v] != 0:
                neighbors += [(u, v)]

        # A node with less than 2 neighbors can always be removed
        if len(neighbors) < 2:
            return True

        # Flood fill from one neighbor `start` to see if we can
        # still reach all the others (without going through x,y)
        start = neighbors[0]
        neighbors = neighbors[1:]
        # 0 = vacant
        # 1 = unvisited
        # 2 = visited
        grid[x][y] = 0
        grid[start[0]][start[1]] = 2
        i = 0
        visited = [start]
        # Early terminate if all remaining neighbors found
        while i < len(visited) and len(neighbors):
            site = visited[i]
            i += 1
            for d in dirs:
                u, v = site[0] + d[0], site[1] + d[1]
                if u < 0 or u >= self.L:
                    continue
                if v < 0 or v >= self.L:
                    continue
                if grid[u][v] == 1:
                    grid[u][v] = 2
                    visited += [(u, v)]
                    if (u, v) in neighbors:
                        neighbors.remove((u, v))

        # Replace the site x,y we artificially removed above
        grid[x][y] = 1

        # Reset all the nodes visited from 2 back to 1
        for u, v in visited:
            grid[u][v] = 1

        # Return whether all neighbors were visited
        return len(neighbors) == 0

    def print_ascii(self, grid: Grid) -> None:
        """Print a grid with ascii characters.

        This renders a grid using 'o' for occupied sites and ascii characters
        such as '-', '|', '\\', '/', 'X' to denote the connections.

        Expects the grid to be populated with {None | `id`} and have a sentinel
        row and column.

        Only valid when radius of interaction is smaller than 2.
        """
        # check if connections are only within the Union-Jack grid
        if self.r > 2 - 0.001:
            print(
                f"[WARN] ASCII art shows only connections up to r < 2 (here r={self.r})"
            )
        ascii_str = "\n"
        for y in range(self.L):
            if y > 0:
                for x in range(self.L):
                    a = grid[x - 1][y - 1]
                    b = grid[x - 1][y]
                    c = grid[x][y - 1]
                    d = grid[x][y]
                    down = a is not None and d is not None
                    up = b is not None and c is not None
                    vert = c is not None and d is not None
                    if up and down:
                        ascii_str += "X"
                    elif up:
                        ascii_str += "/"
                    elif down:
                        ascii_str += "\\"
                    else:
                        ascii_str += " "
                    if vert:
                        ascii_str += "|"
                    else:
                        ascii_str += " "
                ascii_str += "\n"
            for x in range(self.L):
                if grid[x][y] is None:
                    ascii_str += "  "
                elif grid[x - 1][y] is None:
                    ascii_str += " o"
                else:
                    ascii_str += "-o"
            ascii_str += " \n"
        print(ascii_str)
