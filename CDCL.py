import copy
from collections import defaultdict
import time


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
    Returns updated clauses or raises a conflict exception if a conflict occurs.
    """
    new_clauses = {}
    for key, clause in clauses.items():
        if literal in clause:
            continue  # Clause is satisfied
        if -literal in clause:
            new_clause = [l for l in clause if l != -literal]
            if not new_clause:
                # Conflict: Empty clause created
                raise ValueError("Conflict detected while solving literal.")
            new_clauses[key] = new_clause
        else:
            new_clauses[key] = clause
    return new_clauses


def get_copied_clauses(clauses):
    """
    Returns a deep copy of the clauses.
    """
    return copy.deepcopy(clauses)


def resolve_clauses(clause1, clause2, pivot):
    """
    Resolves two clauses on the pivot variable.
    Returns the resolved clause.
    """
    resolved = list(set(clause1 + clause2) - {pivot, -pivot})
    return resolved


class CDCL:
    """
    Implements the CDCL (Conflict-Driven Clause Learning) algorithm for SAT solving.
    """

    def __init__(self, clauses):
        self.clauses = clauses
        self.num_evaluations = 0
        self.num_backtracking = 0
        self.variable_history = []
        self.decision_stack = []  # Tracks decisions for backjumping

    def __is_satisfied__(self):
        """Checks if the problem is satisfied."""
        if not self.clauses:
            return True
        if any(len(clause) == 0 for clause in self.clauses.values()):
            return False
        return None

    def __simplify__(self, var_assignments):
        """Simplifies the problem using unit propagation."""
        while True:
            unit_literals = get_unit_literals(self.clauses)
            if not unit_literals:
                break
            for literal in unit_literals:
                var_assignments[abs(literal)] = literal > 0
                try:
                    self.clauses = solve_literal(self.clauses, literal)
                except ValueError:
                    # Return False if a conflict is detected
                    return False
        return True

    def __choose_next_var__(self, var_assignments):
        """Chooses the next variable to assign."""
        all_vars = get_all_variables(self.clauses)
        for var in all_vars:
            if var not in var_assignments:
                return var
        return None

    def __analyze_conflict(self):
        """
        Analyzes a conflict and generates a learned clause.
        """
        if not self.decision_stack:
            raise ValueError("No decisions made to analyze.")

        # Use the last conflict clause
        conflict_clause = list(self.clauses.values())[0]

        # Initialize the learned clause with the conflict clause
        learned_clause = conflict_clause[:]

        # Resolve with decisions in reverse order until a backtracking level is determined
        while self.decision_stack:
            decision_literal, _ = self.decision_stack.pop()
            learned_clause = resolve_clauses(learned_clause, [decision_literal], abs(decision_literal))

            # Check if the learned clause is asserting at a lower decision level
            if len(learned_clause) == 1 or all(lit not in self.decision_stack for lit in learned_clause):
                break

        return learned_clause

    def __solve__(self, var_assignments):
        """Recursively solves the SAT problem with enhanced backtracking and clause learning."""
        self.num_evaluations += 1

        # Unit propagation and simplification
        if not self.__simplify__(var_assignments):
            # Conflict detected, analyze and learn from it
            learned_clause = self.__analyze_conflict()
            self.clauses[len(self.clauses)] = learned_clause  # Add learned clause to the formula
            self.num_backtracking += 1  # Increment backtracking count
            return False, var_assignments

        # Check if the problem is satisfied
        satisfied = self.__is_satisfied__()
        if satisfied is not None:
            return satisfied, var_assignments

        # Save current state before making a decision
        prev_clauses = get_copied_clauses(self.clauses)
        prev_assignments = var_assignments.copy()

        # Choose the next variable
        var = self.__choose_next_var__(var_assignments)
        if var is None:
            return True, var_assignments

        for value in [True, False]:
            var_assignments[var] = value
            self.decision_stack.append((var if value else -var, "decision"))
            try:
                # Simplify clauses based on the decision
                self.clauses = solve_literal(self.clauses, var if value else -var)

                # Recursively solve with the updated state
                satisfiable, assignments = self.__solve__(var_assignments)
                if satisfiable:
                    return satisfiable, assignments
            except ValueError:
                # Conflict occurred, learn a clause and backtrack
                learned_clause = self.__analyze_conflict()
                self.clauses[len(self.clauses)] = learned_clause
                self.num_backtracking += 1

            # Restore state to backtrack
            var_assignments = prev_assignments.copy()
            self.clauses = get_copied_clauses(prev_clauses)

        return False, var_assignments

    def solve(self):
        """Runs the CDCL algorithm with detailed output."""
        print("\nStarting CDCL solver...")
        start_time = time.time()

        try:
            result, assignments = self.__solve__({})
            end_time = time.time()
            elapsed_time = end_time - start_time

            print("\tSolver finished!")
            print(f"Status: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
            print(f"Time taken: {elapsed_time:.2f} seconds")
            print(f"Number of evaluations: {self.num_evaluations}")
            print(f"Number of backtracks: {self.num_backtracking}")


            return result, assignments, self.num_evaluations, self.num_backtracking

        except KeyboardInterrupt:
            print("\nSolver interrupted by user")
            elapsed_time = time.time() - start_time
            print(f"Time elapsed: {elapsed_time:.2f} seconds")
            print(f"Evaluations: {self.num_evaluations}")
            print(f"Backtracks: {self.num_backtracking}")
            return False, {}, self.num_evaluations, self.num_backtracking