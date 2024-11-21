import random

def generate_sudoku_cnf(puzzle, rules_file, output_file):
    """
    Generates a CNF file for a given Sudoku puzzle.

    :param puzzle: 2D list (9x9) of integers (0 for empty, 1-9 for known values).
    :param rules_file: Path to the file containing Sudoku rules in CNF.
    :param output_file: Path to the output CNF file.
    """
    with open(rules_file, 'r') as rf:
        rules = rf.readlines()
    
    # Extract problem definition and base rules
    p_line = rules[0]
    base_rules = rules[1:]
    
    # Add puzzle-specific constraints
    puzzle_clauses = []
    for r in range(4):
        for c in range(4):
            if puzzle[r][c] != 0:
                variable = 100 * (r + 1) + 10 * (c + 1) + puzzle[r][c]
                puzzle_clauses.append(f"{variable} 0\n")
    
    # Update number of clauses
    total_clauses = len(base_rules) + len(puzzle_clauses)
    p_line = f"p cnf 444 {total_clauses}\n"
    
    # Write to output file
    with open(output_file, 'w') as of:
        of.write(p_line)
        of.writelines(base_rules)
        of.writelines(puzzle_clauses)

def parse_sudoku_txt(file_path):
    """
    Parses a TXT file containing multiple Sudoku puzzles into a list of 9x9 grids.

    :param file_path: Path to the TXT file containing Sudoku puzzles as single lines.
    :return: List of 9x9 grids (each grid is a list of lists).
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    puzzles = []
    for line in lines:
        line = line.strip()
        if len(line) == 16:  # Ensure valid 9x9 grid
            grid = [[int(c) if c.isdigit() else 0 for c in line[i:i+4]] for i in range(0, 16, 4)]
            puzzles.append(grid)
    return puzzles

# Example usage
def main():
    txt_file = "4x4.txt"  # Input TXT file
    rules_file = "sudoku-rules-4x4.txt"  # Sudoku rules in CNF format
    output_folder = "output_cnfs/"  # Folder to save CNF files

    # Parse Sudoku puzzles from TXT file
    puzzles = parse_sudoku_txt(txt_file)

    # Generate CNF for each puzzle
    for idx, puzzle in enumerate(puzzles):
        output_file = f"{output_folder}4x4_{idx + 1}.cnf"
        generate_sudoku_cnf(puzzle, rules_file, output_file)
        print(f"Generated CNF for Sudoku {idx + 1}: {output_file}")

if __name__ == "__main__":
    main()
