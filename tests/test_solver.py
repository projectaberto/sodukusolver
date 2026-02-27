#!/usr/bin/env python3
"""
Unit tests for Sudoku Solver.
Run: python -m unittest discover tests
or:  python tests/test_solver.py
"""

import unittest
from solver import (
    parse_grid,
    count_clues,
    solve_sudoku,
    get_difficulty,
    grid_to_string,
)


class TestSudokuSolver(unittest.TestCase):
    """Test sudoku solver core functionality."""
    
    def test_parse_valid_puzzle(self):
        """Test parsing valid puzzle string."""
        puzzle = """53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79"""
        grid = parse_grid(puzzle)
        self.assertIsNotNone(grid)
        self.assertEqual(len(grid), 9)
        self.assertEqual(len(grid[0]), 9)
        self.assertEqual(grid[0][0], 5)
        self.assertEqual(grid[0][1], 3)
        self.assertEqual(grid[0][2], 0)  # . becomes 0
    
    def test_parse_invalid_dimensions(self):
        """Test parsing fails with wrong dimensions."""
        puzzle = "53..7....\n6..195..."  # Only 2 lines
        grid = parse_grid(puzzle)
        self.assertIsNone(grid)
    
    def test_parse_invalid_characters(self):
        """Test parsing fails with invalid characters."""
        puzzle = """53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..7a"""  # 'a' is invalid
        grid = parse_grid(puzzle)
        self.assertIsNone(grid)
    
    def test_count_clues(self):
        """Test clue counting."""
        puzzle = """53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79"""
        grid = parse_grid(puzzle)
        clues = count_clues(grid)
        self.assertEqual(clues, 29)
    
    def test_solve_known_puzzle(self):
        """Test solving a known puzzle."""
        puzzle = """53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79"""
        grid = parse_grid(puzzle)
        solution, time_ms, backtracks = solve_sudoku(grid)
        
        self.assertIsNotNone(solution)
        self.assertGreater(time_ms, 0)
        self.assertGreater(backtracks, 0)
        
        # Check solution is complete (all cells filled)
        for row in solution:
            for cell in row:
                self.assertGreater(cell, 0)
                self.assertLessEqual(cell, 9)
    
    def test_solve_unsolvable(self):
        """Test that unsolvable puzzle returns None."""
        # All 1s - unsolvable
        puzzle = "1" * 81
        grid = parse_grid(puzzle)
        solution, time_ms, backtracks = solve_sudoku(grid)
        
        self.assertIsNone(solution)
    
    def test_parse_grid_none(self):
        """Test solve_sudoku handles None grid gracefully."""
        solution, time_ms, backtracks = solve_sudoku(None)
        self.assertIsNone(solution)
        self.assertEqual(time_ms, 0)
        self.assertEqual(backtracks, 0)
    
    def test_difficulty_easy(self):
        """Test difficulty classification for easy."""
        # Easy: >= 36 clues AND <= 50 backtracks
        name, emoji = get_difficulty(40, 30)
        self.assertEqual(name, 'Easy')
        self.assertEqual(emoji, '🟢')
    
    def test_difficulty_medium(self):
        """Test difficulty classification for medium."""
        # Medium: 32-35 clues OR 51-500 backtracks
        name, emoji = get_difficulty(33, 60)
        self.assertEqual(name, 'Medium')
        self.assertEqual(emoji, '🟡')
    
    def test_difficulty_hard(self):
        """Test difficulty classification for hard."""
        # Hard: 28-31 clues OR 501-5000 backtracks
        name, emoji = get_difficulty(29, 1000)
        self.assertEqual(name, 'Hard')
        self.assertEqual(emoji, '🟠')
    
    def test_difficulty_expert(self):
        """Test difficulty classification for expert."""
        # Expert: <= 27 clues OR > 5000 backtracks
        name, emoji = get_difficulty(25, 1000)
        self.assertEqual(name, 'Expert')
        self.assertEqual(emoji, '🔴')
    
    def test_grid_to_string(self):
        """Test grid-to-string conversion."""
        puzzle = """53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79"""
        grid = parse_grid(puzzle)
        result = grid_to_string(grid)
        
        expected_lines = [
            '53.7....',
            '6..195...',
            '.98....6.',
            '8...6...3',
            '4..8.3..1',
            '7...2...6',
            '.6....28.',
            '...419..5',
            '....8..79'
        ]
        
        result_lines = result.split('\n')
        for i, line in enumerate(result_lines):
            self.assertEqual(line[0:9], expected_lines[i])


if __name__ == '__main__':
    unittest.main()
