# dimacs_parser.py
def parse_dimacs(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    clauses = []
    num_vars = 0

    for line in lines:
        line = line.strip()
        if line == '' or line.startswith('c'):  # Ignore comments and empty lines
            continue
        elif line.startswith('p'):  # Problem line
            parts = line.split()
            num_vars = int(parts[2])
        else:  # Clause line
            clause = list(map(int, line.rstrip(' 0').split()))
            clauses.append(clause)

    return num_vars, clauses
