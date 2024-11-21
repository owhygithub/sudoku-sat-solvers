import os
from CDCL import parse_cnf,CDCL
from DPLL import DPLL
from JW import JW

# Files provided by the user
cnf_files = [
    "sudoku1.cnf",
    "sudoku2.cnf",
    "sudoku3.cnf",
    "sudoku4.cnf",
    "sudoku5.cnf"
]

# Code to test the provided CNF solver on the uploaded files
def test_cdcl_solver_on_cnf_files(cnf_files):
    from collections import defaultdict
    
    results = defaultdict(dict)
    
    for file_path in cnf_files:
        try:
            # Parse CNF file
            clauses, num_vars = parse_cnf(file_path)
            
            # Initialize the CDCL solver
            solver = CDCL(clauses)
            
            # Solve the problem
            result, assignments = solver.solve()
            print(result)
            
            # Store results
            results[os.path.basename(file_path)]["status"] = "SATISFIABLE" if result else "UNSATISFIABLE"
            results[os.path.basename(file_path)]["assignments"] = assignments if result else None
        except Exception as e:
            results[os.path.basename(file_path)]["error"] = str(e)
    
    return results

def test_DPLL_solver_on_cnf_files(cnf_files):
    from collections import defaultdict
    
    results = defaultdict(dict)
    
    for file_path in cnf_files:
        try:
            # Parse CNF file
            clauses, num_vars = parse_cnf(file_path)
            
            # Initialize the DPLL solver
            solver = DPLL(clauses)
            
            # Solve the problem
            result, assignments = solver.solve()
            print(result)
            
            # Store results
            results[os.path.basename(file_path)]["status"] = "SATISFIABLE" if result else "UNSATISFIABLE"
            results[os.path.basename(file_path)]["assignments"] = assignments if result else None
        except Exception as e:
            results[os.path.basename(file_path)]["error"] = str(e)
    
    return results

def test_JW_solver_on_cnf_files(cnf_files):
    from collections import defaultdict
    
    results = defaultdict(dict)
    
    for file_path in cnf_files:
        try:
            # Parse CNF file
            clauses, num_vars = parse_cnf(file_path)
            
            # Initialize the JW solver
            solver = JW(clauses)
            
            # Solve the problem
            result, assignments = solver.solve()
            print(result)
            
            # Store results
            results[os.path.basename(file_path)]["status"] = "SATISFIABLE" if result else "UNSATISFIABLE"
            results[os.path.basename(file_path)]["assignments"] = assignments if result else None
        except Exception as e:
            results[os.path.basename(file_path)]["error"] = str(e)
    
    return results

# # Execute the testing
# results = test_cdcl_solver_on_cnf_files(cnf_files)
# results

# results = test_DPLL_solver_on_cnf_files(cnf_files)
# results

# Execute the testing
results = test_JW_solver_on_cnf_files(cnf_files)
results