import random

def generate_sudoku_clauses(grid_size, num_clues=17):
    clauses = []

    def var(i, j, k):
        return grid_size * grid_size * (i - 1) + grid_size * (j - 1) + k

    # Standard Sudoku constraints (cell, row, column, sub-grid)
    for i in range(1, grid_size + 1):
        for j in range(1, grid_size + 1):
            clauses.append([var(i, j, k) for k in range(1, grid_size + 1)])
            for k1 in range(1, grid_size + 1):
                for k2 in range(k1 + 1, grid_size + 1):
                    clauses.append([-var(i, j, k1), -var(i, j, k2)])

    for i in range(1, grid_size + 1):
        for k in range(1, grid_size + 1):
            for j1 in range(1, grid_size + 1):
                for j2 in range(j1 + 1, grid_size + 1):
                    clauses.append([-var(i, j1, k), -var(i, j2, k)])

    box_size = int(grid_size ** 0.5)
    for k in range(1, grid_size + 1):
        for box_i in range(0, box_size):
            for box_j in range(0, box_size):
                cells = [
                    var(box_i * box_size + di + 1, box_j * box_size + dj + 1, k)
                    for di in range(box_size) for dj in range(box_size)
                ]
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        clauses.append([-cells[i], -cells[j]])

    # Add predefined clues for solvable puzzles
    predefined_clauses = []
    while len(predefined_clauses) < num_clues:
        i = random.randint(1, grid_size)
        j = random.randint(1, grid_size)
        k = random.randint(1, grid_size)
        predefined_clauses.append([var(i, j, k)])
    clauses += predefined_clauses

    return clauses
