#!/usr/bin/env python3
"""
Sudoku Solver Portal - Core solver and automation engine.
Python 3.12, zero external dependencies.
"""

import os
import re
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path


# ============================================================================
# Sudoku Solver
# ============================================================================

def parse_grid(puzzle_str):
    """
    Parse puzzle string into 9x9 grid.
    
    Input: 9 lines, 9 chars each (1-9 or . for empty)
    Output: 2D list (0=empty, 1-9=clue)
    Returns None if invalid format.
    """
    lines = puzzle_str.strip().split('\n')
    
    if len(lines) != 9:
        return None
    
    grid = []
    for line in lines:
        if len(line) != 9:
            return None
        
        row = []
        for char in line:
            if char == '.':
                row.append(0)
            elif char.isdigit() and 1 <= int(char) <= 9:
                row.append(int(char))
            else:
                return None
        grid.append(row)
    
    return grid


def count_clues(grid):
    """Count number of given clues in the grid."""
    if grid is None:
        return 0
    return sum(1 for row in grid for cell in row if cell != 0)


def is_valid(grid, row, col, num):
    """Check if placing num at grid[row][col] is valid."""
    # Check row
    if num in grid[row]:
        return False
    
    # Check column
    if num in [grid[i][col] for i in range(9)]:
        return False
    
    # Check 3x3 box
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if grid[i][j] == num:
                return False
    
    return True


def solve_sudoku(grid):
    """
    Solve sudoku using backtracking.
    
    Returns: (solution_grid, time_ms, backtrack_count)
    solution_grid is None if unsolvable.
    """
    if grid is None:
        return None, 0, 0
    
    # Deep copy
    grid = [row[:] for row in grid]
    
    start_time = time.perf_counter()
    backtrack_count = [0]  # Use list to allow modification in nested function
    
    def backtrack(pos):
        if pos == 81:
            return True
        
        row, col = pos // 9, pos % 9
        
        if grid[row][col] != 0:
            return backtrack(pos + 1)
        
        for num in range(1, 10):
            if is_valid(grid, row, col, num):
                grid[row][col] = num
                if backtrack(pos + 1):
                    return True
                grid[row][col] = 0
                backtrack_count[0] += 1
        
        return False
    
    solved = backtrack(0)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    if solved:
        return grid, elapsed_ms, backtrack_count[0]
    else:
        return None, elapsed_ms, backtrack_count[0]


def get_difficulty(clues, backtracks):
    """Determine difficulty level based on clues and backtracks."""
    # Easy: >= 36 clues AND <= 50 backtracks
    if clues >= 36 and backtracks <= 50:
        return ('Easy', '🟢')
    
    # Expert: <= 27 clues OR > 5000 backtracks
    if clues <= 27 or backtracks > 5000:
        return ('Expert', '🔴')
    
    # Hard: 28-31 clues OR 501-5000 backtracks
    if (28 <= clues <= 31) or (501 <= backtracks <= 5000):
        return ('Hard', '🟠')
    
    # Medium: 32-35 clues OR 51-500 backtracks
    if (32 <= clues <= 35) or (51 <= backtracks <= 500):
        return ('Medium', '🟡')
    
    return ('Unknown', '❓')


def format_grid_display(grid):
    """Format grid for display with borders."""
    if grid is None:
        return None
    
    lines = []
    for row_idx, row in enumerate(grid):
        if row_idx > 0 and row_idx % 3 == 0:
            lines.append('------+-------+------')
        
        parts = []
        for col_idx, cell in enumerate(row):
            if col_idx > 0 and col_idx % 3 == 0:
                parts.append('|')
            parts.append(str(cell))
        
        lines.append(' '.join(parts))
    
    return '\n'.join(lines)


def grid_to_string(grid):
    """Convert grid to 9-line string format (for history)."""
    if grid is None:
        return None
    
    lines = []
    for row in grid:
        lines.append(''.join(str(cell) for cell in row))
    return '\n'.join(lines)


def get_git_info():
    """Get current commit SHA and timestamp."""
    try:
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        return sha
    except Exception:
        return 'unknown'


def get_previous_solution():
    """Read previous solution metadata from README if exists."""
    readme_path = Path('README.md')
    if not readme_path.exists():
        return None
    
    try:
        content = readme_path.read_text()
        # Try to extract metadata from last solve block
        match = re.search(r'<!-- SUDOKU-START -->.*?<!-- SUDOKU-END -->', content, re.DOTALL)
        if match:
            return match.group(0)
    except Exception:
        pass
    
    return None


def create_history_file(original_grid, solution_grid, clues, backtracks, time_ms, sha):
    """Create history file with full metadata."""
    difficulty_name, difficulty_emoji = get_difficulty(clues, backtracks)
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    original_str = grid_to_string(original_grid)
    solution_str = grid_to_string(solution_grid)
    solution_display = format_grid_display(solution_grid)
    
    content = f"""# Sudoku Solution - {timestamp}

**Metadata**
- Solved at: {timestamp} UTC
- Commit: {sha}
- Difficulty: {difficulty_emoji} {difficulty_name}
- Clues: {clues}
- Backtracks: {backtracks}
- Time: {time_ms:.2f} ms

**Original Puzzle**
```
{original_str}
```

**Solution**
```
{solution_display}
```

**Solution (compact)**
```
{solution_str}
```
"""
    return content, timestamp


def prune_history(max_keep):
    """Remove oldest history files if count exceeds max_keep."""
    history_dir = Path('history')
    if not history_dir.exists():
        return
    
    files = sorted(history_dir.glob('solve-*.md'), reverse=True)
    
    for old_file in files[max_keep:]:
        try:
            old_file.unlink()
        except Exception:
            pass


def update_readme(original_grid, solution_grid, clues, backtracks, time_ms, sha):
    """Update README with latest solution."""
    difficulty_name, difficulty_emoji = get_difficulty(clues, backtracks)
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    solution_display = format_grid_display(solution_grid)
    original_str = grid_to_string(original_grid)
    
    solve_section = f"""<!-- SUDOKU-START -->

**Latest Solve** • Solved in {time_ms:.0f} ms • Difficulty: {difficulty_emoji} {difficulty_name} • Backtracks: {backtracks} • Clues: {clues}

{solution_display}

**Original Puzzle**

{original_str}

Last solved: {timestamp} UTC (commit {sha})  
View recent solves → ./history/

<!-- SUDOKU-END -->"""
    
    readme_path = Path('README.md')
    if readme_path.exists():
        content = readme_path.read_text()
        # Replace or insert solve section
        if '<!-- SUDOKU-START -->' in content:
            content = re.sub(
                r'<!-- SUDOKU-START -->.*?<!-- SUDOKU-END -->',
                solve_section,
                content,
                flags=re.DOTALL
            )
        else:
            # Append before final marker if exists, else append
            if 'Wubba lubba dub dub' in content:
                content = content.replace('Wubba lubba dub dub', f'{solve_section}\n\nWubba lubba dub dub')
            else:
                content += f'\n\n{solve_section}'
    else:
        content = f"""# Sudoku Solver Portal

Public 9×9 Sudoku solver running in GitHub Actions.  
Submit puzzles easily via the web editor or by editing puzzle/current.txt → open PR → auto-merges if only that file changed.

### Submit a Puzzle

Visit the web editor at https://projectaberto.github.io/sudokusolver/ to fill the grid visually.

---

   ~~~~~ Wubba Lubba Dub Dub ~~~~~ [burp] ~~~~~
   ╔═══════════════════[ Latest Solve Portal ]═══════════════════╗

{solve_section}

Wubba lubba dub dub! 🚀
"""
    
    readme_path.write_text(content)


def update_readme_error(error_msg, original_str, sha):
    """Update README with error entry instead of solution."""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    error_section = f"""<!-- SUDOKU-START -->

**Error** ⚠️ Could not solve puzzle

{error_msg}

**Original Puzzle**

{original_str}

Last attempt: {timestamp} UTC (commit {sha})

<!-- SUDOKU-END -->"""
    
    readme_path = Path('README.md')
    if readme_path.exists():
        content = readme_path.read_text()
        if '<!-- SUDOKU-START -->' in content:
            content = re.sub(
                r'<!-- SUDOKU-START -->.*?<!-- SUDOKU-END -->',
                error_section,
                content,
                flags=re.DOTALL
            )
        else:
            if 'Wubba lubba dub dub' in content:
                content = content.replace('Wubba lubba dub dub', f'{error_section}\n\nWubba lubba dub dub')
            else:
                content += f'\n\n{error_section}'
    else:
        content = f"""# Sudoku Solver Portal

Public 9×9 Sudoku solver running in GitHub Actions.

---

   ~~~~~ Wubba Lubba Dub Dub ~~~~~ [burp] ~~~~~
   ╔═══════════════════[ Latest Solve Portal ]═══════════════════╗

{error_section}

Wubba lubba dub dub! 🚀
"""
    
    readme_path.write_text(content)


def main():
    """Main entry point."""
    puzzle_path = Path('puzzle/current.txt')
    
    if not puzzle_path.exists():
        print('ERROR: puzzle/current.txt not found')
        sys.exit(1)
    
    # Read puzzle
    try:
        puzzle_str = puzzle_path.read_text()
    except Exception as e:
        print(f'ERROR reading puzzle: {e}')
        sys.exit(1)
    
    # Parse grid
    original_grid = parse_grid(puzzle_str)
    if original_grid is None:
        sha = get_git_info()
        update_readme_error(
            'Invalid puzzle format: must be 9×9 grid with digits 1-9 or . (empty)',
            puzzle_str.strip(),
            sha
        )
        print('ERROR: Invalid puzzle format')
        sys.exit(1)
    
    # Solve
    solution_grid, time_ms, backtracks = solve_sudoku(original_grid)
    
    if solution_grid is None:
        sha = get_git_info()
        clues = count_clues(original_grid)
        update_readme_error(
            f'Puzzle is unsolvable (has {clues} clues)',
            puzzle_str.strip(),
            sha
        )
        print('ERROR: Puzzle unsolvable')
        sys.exit(1)
    
    # Success: update README and history
    clues = count_clues(original_grid)
    sha = get_git_info()
    
    update_readme(original_grid, solution_grid, clues, backtracks, time_ms, sha)
    
    # Create history file
    history_content, timestamp = create_history_file(
        original_grid, solution_grid, clues, backtracks, time_ms, sha
    )
    
    history_path = Path('history') / f'solve-{datetime.utcnow().strftime("%Y%m%d-%H%M%S")}-{sha}.md'
    history_path.write_text(history_content)
    
    # Prune history
    max_keep = int(os.environ.get('MAX_HISTORY_KEEP', '50'))
    prune_history(max_keep)
    
    print(f'✓ Solved in {time_ms:.0f} ms ({backtracks} backtracks)')
    print(f'✓ Clues: {clues}, Difficulty: {get_difficulty(clues, backtracks)[0]}')
    print('✓ README updated')
    print(f'✓ History archived ({history_path.name})')


if __name__ == '__main__':
    main()
