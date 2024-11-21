import time
from sat_solver import DPLLSolver, JWSolver, CDCLSolver
from dimacs_generator import generate_sudoku_clauses

def run_experiment():
    results = {"4x4": {}, "9x9": {}}
    solvers = [DPLLSolver, JWSolver, CDCLSolver]
    solver_names = ["DPLL", "JW", "CDCL"]

    for grid_size, key in [(4, "4x4"), (9, "9x9")]:
        clauses = generate_sudoku_clauses(grid_size)
        num_vars = grid_size ** 3

        for solver, name in zip(solvers, solver_names):
            start_time = time.time()
            solver_instance = solver(clauses, num_vars)
            solver_instance.solve()
            elapsed_time = time.time() - start_time

            results[key][name] = elapsed_time
            print(f"{name} on {key}: {elapsed_time:.2f}s")

    print("\nFinal Results:")
    for key, timings in results.items():
        print(f"{key} Sudoku:")
        for solver, time_taken in timings.items():
            print(f"  {solver}: {time_taken:.2f}s")

if __name__ == "__main__":
    run_experiment()
