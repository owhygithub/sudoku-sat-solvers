import time
from collections import Counter

class SATSolverBase:
    def __init__(self, clauses, num_vars):
        self.clauses = clauses
        self.num_vars = num_vars
        self.assignment = {}

    def is_satisfied(self, clause):
        return any(self.assignment.get(abs(lit), lit > 0) == (lit > 0) for lit in clause)

    def is_unsatisfied(self, clause):
        return all(self.assignment.get(abs(lit), lit > 0) != (lit > 0) for lit in clause)

    def all_satisfied(self):
        return all(self.is_satisfied(clause) for clause in self.clauses)

    def any_unsatisfied(self):
        return any(self.is_unsatisfied(clause) for clause in self.clauses)

    def unassigned_vars(self):
        return {abs(lit) for clause in self.clauses for lit in clause} - self.assignment.keys()

    def get_solution(self):
        return [f"{var if self.assignment.get(var, False) else -var} 0" for var in range(1, self.num_vars + 1)]


class DPLLSolver(SATSolverBase):
    def solve(self):
        return self.dpll()

    def dpll(self):
        if self.all_satisfied():
            return True
        if self.any_unsatisfied():
            return False

        var = next(iter(self.unassigned_vars()))  # Choose first unassigned variable
        for value in [True, False]:
            self.assignment[var] = value
            if self.dpll():
                return True
            del self.assignment[var]

        return False


class JWSolver(SATSolverBase):
    def solve(self):
        return self.dpll()

    def jw_heuristic(self):
        # Jeroslow-Wang heuristic: prioritize variables in smaller clauses
        weights = Counter()
        for clause in self.clauses:
            for lit in clause:
                if abs(lit) not in self.assignment:
                    weights[abs(lit)] += 2 ** -len(clause)
        return weights.most_common(1)[0][0] if weights else None

    def dpll(self):
        if self.all_satisfied():
            return True
        if self.any_unsatisfied():
            return False

        var = self.jw_heuristic()  # Choose variable using JW heuristic
        for value in [True, False]:
            self.assignment[var] = value
            if self.dpll():
                return True
            del self.assignment[var]

        return False


class CDCLSolver(SATSolverBase):
    def __init__(self, clauses, num_vars):
        super().__init__(clauses, num_vars)
        self.learned_clauses = []

    def solve(self):
        return self.cdcl()

    def cdcl(self):
        decision_stack = []
        while True:
            # Propagate and check for conflicts
            conflict = self.propagate()
            if conflict:
                learned_clause = self.analyze_conflict(conflict)
                if not learned_clause:
                    return False
                self.learned_clauses.append(learned_clause)
                decision_stack.pop()  # Backtrack
            elif self.all_satisfied():
                return True
            else:
                var = next(iter(self.unassigned_vars()))  # Decision heuristic
                decision_stack.append(var)
                self.assignment[var] = True

    def propagate(self):
        for clause in self.clauses + self.learned_clauses:
            if len([lit for lit in clause if abs(lit) in self.assignment]) == 1:
                for lit in clause:
                    if abs(lit) not in self.assignment:
                        self.assignment[abs(lit)] = (lit > 0)
        return None  # No conflict

    def analyze_conflict(self, conflict):
        # Basic conflict analysis: return a new learned clause
        return [-lit for lit in conflict]
