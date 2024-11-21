import os
import time
import numpy as np
import csv
from collections import defaultdict
from CDCL import parse_cnf, CDCL
from DPLL import DPLL
from JW import JW
import json
import multiprocessing

TIME_LIMIT = 150  # Updated Time limit for solving the Sudoku in seconds

def solve_with_timeout(solver_class, cnf_file, result_dict, timeout):
    """
    A function to run the solver with a timeout. It runs the solver, 
    and stores the result in a shared dictionary.
    """
    try:
        # Parse CNF file
        clauses, num_vars = parse_cnf(cnf_file)

        # Initialize the solver
        solver = solver_class(clauses)

        # Start timer
        start_time = time.time()

        # Solve the problem
        result, assignments, evals, backtracks = solver.solve()

        # Time taken
        time_taken = time.time() - start_time

        # Check if the solver exceeded the time limit
        if time_taken > TIME_LIMIT:
            result = False  # Timeout: Mark as UNSATISFIABLE
            result_dict['status'] = "UNSATISFIABLE"
            print(f"Timeout: Solver took {time_taken:.2f} seconds, marking as UNSATISFIABLE.")
        else:
            result_dict['status'] = "SATISFIABLE"

        result_dict['time_taken'] = time_taken
        result_dict['assignments'] = assignments
        result_dict['evaluations'] = evals
        result_dict['backtracks'] = backtracks

    except Exception as e:
        result_dict['status'] = "ERROR"
        result_dict['error'] = str(e)

def print_solution(assignment):
    """
    Print the Sudoku solution in a readable grid format.
    """
    grid = [[0 for _ in range(9)] for _ in range(9)]

    for var, value in assignment.items():
        if value and 100 <= var <= 999:
            row = (var // 100) - 1
            col = ((var // 10) % 10) - 1
            digit = var % 10
            grid[row][col] = digit

    print("\nSudoku Solution:")
    print("  " + "-" * 25)
    for i, row in enumerate(grid):
        if i % 3 == 0 and i != 0:
            print("  " + "-" * 25)
        row_str = "  |"
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                row_str += "|"
            row_str += f" {val}"
        row_str += " |"
        print(row_str)
    print("  " + "-" * 25)

def save_results_to_file(results, file_path):
    with open(file_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {file_path}")

def extract_sudoku_info(file_path):
    """
    Extracts the sudoku number and size from the CNF file name.
    """
    filename = os.path.basename(file_path)
    parts = filename.split("_")
    sudoku_size = parts[1] if len(parts) > 1 else "Unknown"
    sudoku_number = parts[2].split(".")[0] if len(parts) > 2 else "Unknown"
    return sudoku_size, sudoku_number


def save_results_to_json(results, file_path):
    with open(file_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {file_path}")


def save_results_to_csv(results, csv_file, append=False):
    """
    Saves results into a CSV file iteratively.
    The file is opened in append mode if `append=True`.
    """
    fieldnames = ["solver", "grid_size", "sudoku_number", "evaluations", "backtracks", "time_taken", "status"]
    
    # Open the CSV file for appending or writing
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # If the file is empty (i.e., it doesn't exist or it's the first run), write the header
        if file.tell() == 0:
            writer.writeheader()

        # Write the results for each file
        for file_path, data in results.items():
            # print(data)
            for i in range(len(data["solver"])):
                row = {
                    "solver": data["solver"][i],
                    "grid_size": data["grid_size"][i],
                    "sudoku_number": data["sudoku_number"][i],
                    "evaluations": data["evaluations"][i],
                    "backtracks": data["backtracks"][i],
                    "time_taken": data["time_taken"][i],
                    "status": data["status"][i]
                }
                writer.writerow(row)

    print(f"Results saved to CSV: {csv_file}")



def run_solver_experiment(solver_class, cnf_files, solver_name, num_runs=1, save_path="all_results.json", csv_file="experiment_results.csv"):
    results = defaultdict(lambda: defaultdict(list))

    for file_path in cnf_files:
        print(f"\n== Running solver {solver_name} on {file_path}...")

        filename = os.path.basename(file_path)
        parts = filename.split(".")
        parts2 = parts[0]
        parts3 = parts2.split("_")
        grid_size = parts3[0]
        try: 
            sudoku_number = parts3[1]
        except:
            print("*not 9x9 hard")

        result_dict = multiprocessing.Manager().dict()

        # Create a process to run the solver with a timeout
        process = multiprocessing.Process(target=solve_with_timeout, args=(solver_class, file_path, result_dict, TIME_LIMIT))

        # Start the process
        process.start()

        # Wait for the solver to finish (with timeout)
        process.join(TIME_LIMIT)

        if process.is_alive():
            # If the process is still alive after the timeout, terminate it
            process.terminate()
            # print(solver_name, grid_size, sudoku_number, evals, backtracks, time_taken)
            # result_dict['status'] = "UNSATISFIABLE"
            #result_dict['error'] = "Solver exceeded time limit"
            results[file_path]["solver"].append(solver_name)
            results[file_path]["grid_size"].append(grid_size)
            results[file_path]["sudoku_number"].append(sudoku_number)
            results[file_path]["evaluations"].append(evals)
            results[file_path]["backtracks"].append(backtracks)
            results[file_path]["time_taken"].append(time_taken)
            results[file_path]["status"].append("UNSATISFIABLE")
            print("Solver exceeded time limit")

        # try:
        # print("TRYING")
        # Parse CNF file
        else:
            clauses, num_vars = parse_cnf(file_path)

            # Initialize the solver
            solver = solver_class(clauses)

            # Start timer
            start_time = time.time()

            # Solve the problem
            result, assignments, evals, backtracks = solver.solve()

            time_taken = time.time() - start_time

            print_solution(assignments)
            # print("HELLO")

            # Time taken
            # time_taken = time.time() - start_time

            # Store statistics
            # print(solver_name, grid_size, sudoku_number, evals, backtracks, time_taken)

            results[file_path]["solver"].append(solver_name)
            results[file_path]["grid_size"].append(grid_size)
            results[file_path]["sudoku_number"].append(sudoku_number)
            results[file_path]["evaluations"].append(evals)
            results[file_path]["backtracks"].append(backtracks)
            results[file_path]["time_taken"].append(time_taken)
            results[file_path]["status"].append("SATISFIABLE" if result else "UNSATISFIABLE")

        # except Exception as e:
        #     results[file_path]["error"].append(str(e))

    save_results_to_json(results, save_path)
    save_results_to_csv(results, csv_file, append=True)
    # print(results)

    return results


def run_experiment():
    solvers = [
        (CDCL, "CDCL"),
        (DPLL, "DPLL"),
        (JW, "JW")
    ]

    all_results = {}

    for solver_class, solver_name in solvers:
        print(f"\n======= Running experiments for solver: {solver_name}\n")
        results = run_solver_experiment(solver_class, cnf_files, solver_name)
        all_results[solver_name] = results
        print(f"Completed experiments for solver: {solver_name}\n")

    return all_results

if __name__ == "__main__":
    cnf_folder = "output_cnfs"
    cnf_files = sorted(
        [os.path.join(cnf_folder, file) for file in os.listdir(cnf_folder) if file.endswith(".cnf")]
    )

    all_results = run_experiment()
    save_results_to_csv(all_results, "experiment_results.csv")
