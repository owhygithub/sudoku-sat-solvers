import copy
from collections import defaultdict
import time

def calculate_jw_scores(clauses):
    """
    Calculate the Jeroslow-Wang (JW) scores for all literals.
    """
    scores = defaultdict(float)
    for clause in clauses.values():
        clause_size = len(clause)
        weight = 2 ** -clause_size
        for literal in clause:
            scores[literal] += weight
    return scores


def parse_cnf(filename):
    """
    Parse CNF file in DIMACS format.
    Returns clauses as a dictionary and a set of variables.
    """
    clauses = {}
    num_vars = 0
    with open(filename, 'r') as f:
        clause_idx = 0
        for line in f:
            if line.startswith('c'):
                continue
            elif line.startswith('p cnf'):
                parts = line.strip().split()
                num_vars = int(parts[2])
            else:
                clause = [int(x) for x in line.strip().split() if x != '0']
                if clause:
                    clauses[clause_idx] = clause
                    clause_idx += 1
    return clauses, num_vars


def get_all_variables(clauses):
    """
    Extract all unique variables from the clauses.
    """
    return list({abs(lit) for clause in clauses.values() for lit in clause})


def get_unit_literals(clauses):
    """
    Extract all unit literals (clauses of length 1).
    """
    return [clause[0] for clause in clauses.values() if len(clause) == 1]


def solve_literal(clauses, literal):
    """
    Simplify the clauses by solving a literal.
    Returns updated clauses or False if a conflict occurs.
    """
    new_clauses = {}
    for key, clause in clauses.items():
        if literal in clause:
            continue  # Clause is satisfied
        if -literal in clause:
            new_clause = [l for l in clause if l != -literal]
            if not new_clause:
                # Conflict: Empty clause created
                return False
            new_clauses[key] = new_clause
        else:
            new_clauses[key] = clause
    return new_clauses


def get_copied_clauses(clauses):
    """
    Returns a deep copy of the clauses.
    """
    return copy.deepcopy(clauses)


def pure_literal_elimination(clauses):
    """
    Eliminate pure literals from the clauses.
    A literal is pure if it always appears with the same polarity.
    """
    literal_counts = defaultdict(int)
    for clause in clauses.values():
        for lit in clause:
            literal_counts[lit] += 1

    pure_literals = [lit for lit in literal_counts if -lit not in literal_counts]
    for pure_literal in pure_literals:
        clauses = solve_literal(clauses, pure_literal)
        if clauses is False:
            return False
    return clauses


def remove_tautologies(clauses):
    """
    Remove tautological clauses from the CNF formula.
    A clause is tautological if it contains both a literal and its negation.
    """
    new_clauses = {}
    for key, clause in clauses.items():
        if any(-lit in clause for lit in clause):
            continue  # Skip tautological clause
        new_clauses[key] = clause
    return new_clauses


def get_unassigned_variables(var_assignments, clauses):
    """
    Identify unassigned variables from the clauses and variable assignments.
    """
    all_vars = get_all_variables(clauses)
    return [var for var in all_vars if var not in var_assignments]


class JW:
    """
    Implements the JW algorithm for SAT solving with unit propagation,
    pure literal elimination, tautology removal, and proper backtracking.
    """

    def __init__(self, clauses):
        self.clauses = clauses
        self.num_evaluations = 0
        self.num_backtracking = 0
        self.variable_history = []

    def __is_satisfied__(self, var_assignments):
        """
        Checks if the problem is satisfied.
        Additionally ensures all variables are assigned.
        """
        if not self.clauses:
            # Ensure all variables are assigned
            unassigned_vars = get_unassigned_variables(var_assignments, self.clauses)
            if unassigned_vars:
                print(f"Unassigned variables remain: {unassigned_vars}")
                return False
            return True
        if any(len(clause) == 0 for clause in self.clauses.values()):
            return False
        return None

    def __simplify__(self, var_assignments):
        """
        Simplifies the problem using unit propagation, pure literal elimination,
        and tautology removal.
        """
        while True:
            # Unit propagation
            unit_literals = get_unit_literals(self.clauses)
            if not unit_literals:
                break
            for literal in unit_literals:
                var_assignments[abs(literal)] = literal > 0
                self.clauses = solve_literal(self.clauses, literal)
                if self.clauses is False:
                    return False

        # Pure literal elimination
        self.clauses = pure_literal_elimination(self.clauses)
        if self.clauses is False:
            return False

        # Remove tautological clauses
        self.clauses = remove_tautologies(self.clauses)

        return True

    def __choose_next_var__(self, var_assignments):
        """
        Chooses the next variable using the JW heuristic.
        """
        scores = calculate_jw_scores(self.clauses)
        unassigned = get_unassigned_variables(var_assignments, self.clauses)
        if not unassigned:
            return None

        # Combine positive and negative literal scores
        best_var = None
        max_score = float('-inf')
        for var in unassigned:
            score = scores[var] + scores[-var]
            if score > max_score:
                max_score = score
                best_var = var
        return best_var


    def __solve__(self, var_assignments):
        """
        Recursively solves the SAT problem with proper backtracking.
        """
        self.num_evaluations += 1

        # Simplify the formula
        if not self.__simplify__(var_assignments):
            self.num_backtracking += 1
            return False, var_assignments

        # Check if satisfied
        satisfied = self.__is_satisfied__(var_assignments)
        if satisfied is not None:
            return satisfied, var_assignments

        # Save current state before making a decision
        prev_clauses = get_copied_clauses(self.clauses)
        prev_assignments = var_assignments.copy()

        # Choose the next variable to assign
        var = self.__choose_next_var__(var_assignments)
        if var is None:
            return True, var_assignments

        for value in [True, False]:
            var_assignments[var] = value
            self.clauses = solve_literal(self.clauses, var if value else -var)
            if self.clauses is False:
                continue
            satisfiable, assignments = self.__solve__(var_assignments)
            if satisfiable:
                return satisfiable, assignments
            # Backtrack
            var_assignments = prev_assignments.copy()
            self.clauses = get_copied_clauses(prev_clauses)
            self.num_backtracking += 1

        return False, var_assignments

    def solve(self):
        """
        Runs the JW algorithm and returns the result, assignments, and statistics.
        """
        print("\nStarting JW solver...")
        start_time = time.time()

        try:
            result, assignments = self.__solve__({})
            elapsed_time = time.time() - start_time

            print("\tSolver finished!")
            print(f"Status: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
            print(f"Time taken: {elapsed_time:.2f} seconds")
            print(f"Evaluations: {self.num_evaluations}")
            print(f"Backtracks: {self.num_backtracking}")

            # Check for unassigned variables
            if result:
                unassigned_vars = get_unassigned_variables(assignments, self.clauses)
                if unassigned_vars:
                    print(f"Error: Unassigned variables remain: {unassigned_vars}")
                    result = False  # Mark as unsatisfiable

            return result, assignments, self.num_evaluations, self.num_backtracking

        except KeyboardInterrupt:
            elapsed_time = time.time() - start_time
            print("\nSolver interrupted by user")
            print(f"Time elapsed: {elapsed_time:.2f} seconds")
            print(f"Evaluations: {self.num_evaluations}")
            print(f"Backtracks: {self.num_backtracking}")
            return False, {}, self.num_evaluations, self.num_backtracking
