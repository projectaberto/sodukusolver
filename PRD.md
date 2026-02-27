Product Requirements Document – Sudoku Solver Portal

Version: 1.0  
Date: February 20, 2026  
Owner: David

1. Project Goal

Create a public GitHub repository that allows frictionless community Sudoku submissions while keeping the core logic protected. Key behaviors:

- Anyone submits a 9×9 puzzle by editing puzzle/current.txt in a pull request (or via the new web front-end)
- PRs that only change that file are automatically approved and merged (no manual review)
- On merge, GitHub Actions runs a Python solver → updates README with latest result → archives in history/
- History is pruned automatically to prevent unbounded growth
- README shows static intro + fun separator + latest solve only
- A simple static front-end hosted on GitHub Pages provides a visual Sudoku grid editor and one-click submission to GitHub (pre-filling a pull request)

2. Core Constraints & Choices

- Sudoku: classic 9×9 with 3×3 blocks, numbers 1–9
- Language: Python 3.12, single-file solver, zero external dependencies
- Trigger: on: push to main (post-merge), filtered to puzzle/current.txt
- Submission: PR + auto-merge (no direct public pushes to main)
- Difficulty: 🟢 Easy / 🟡 Medium / 🟠 Hard / 🔴 Expert
- History limit: repo variable MAX_HISTORY_KEEP (fallback 50)
- Front-end: static HTML + vanilla JavaScript hosted via GitHub Pages

3. Required Repo Settings (one-time, manual)

General → Pull Requests → Allow auto-merge: enabled  
Branches → Branch protection rule for main:  
  Require pull request before merging: yes  
  Require approvals: 0  
  Require review from Code Owners: yes  
Actions → General → Workflow permissions: Read and write permissions  
Settings → Pages → Source: Deploy from branch main → /site (or root if preferred)

4. File Tree

.
├── .github/
│   ├── CODEOWNERS
│   └── workflows/
│       ├── auto-merge-puzzle-pr.yml
│       └── solve-sudoku.yml
├── history/                          # populated & pruned automatically
│   └── solve-YYYYMMDD-HHMMSS-<full_sha>.md
├── puzzle/
│   └── current.txt                   # 9×9 plain text grid
├── site/                             # GitHub Pages static front-end
│   ├── index.html
│   ├── style.css
│   └── script.js
├── solver.py                         # all logic: parse → solve → stats → README update → prune
├── tests/                            # basic automated tests
│   └── test_solver.py
├── cypress/                          # Cypress E2E config & tests (front-end only)
│   ├── e2e/
│   │   └── submit.cy.js
│   └── support/
├── cypress.config.js                 # Cypress configuration (root)
├── package.json                      # Node.js dependencies (root)
└── README.md

5. CODEOWNERS

*                       @projectaberto  
puzzle/current.txt

6. Puzzle Format (puzzle/current.txt)

9 lines × 9 characters exactly.  
Allowed chars: 1–9 (clues) or . (empty). No spaces, no comments.

Example content:

53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79

7. Auto-Merge Workflow (.github/workflows/auto-merge-puzzle-pr.yml)

name: Auto-Merge Puzzle Submissions

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Determine changed paths
        id: filter
        uses: dorny/paths-filter@v3
        with:
          filters: |
            puzzle_only:
              - 'puzzle/current.txt'
              - '!**'

      - name: Auto-approve if only puzzle changed
        if: steps.filter.outputs.puzzle_only == 'true'
        run: gh pr review ${{ github.event.pull_request.html_url }} --approve --body "Auto-approved: only puzzle/current.txt changed"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Enable auto-merge (squash)
        if: steps.filter.outputs.puzzle_only == 'true'
        run: gh pr merge ${{ github.event.pull_request.html_url }} --auto --squash --body "Auto-merged puzzle submission"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

8. Solver Workflow (.github/workflows/solve-sudoku.yml)

name: Solve Sudoku & Update README

on:
  push:
    branches: [main]
    paths: ['puzzle/current.txt']

jobs:
  test-and-solve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run Python unit tests
        run: python -m unittest discover tests

      - name: Run solver & update files
        env:
          MAX_HISTORY_KEEP: ${{ vars.MAX_HISTORY_KEEP || 50 }}
        run: python solver.py

      - name: Commit & push changes (if any)
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: solved latest puzzle 🔍 [auto]"
          branch: main

9. README Structure

# Sudoku Solver Portal

Public 9×9 Sudoku solver running in GitHub Actions.  
Submit puzzles easily via the web editor below or by editing puzzle/current.txt → open PR → auto-merges if only that file changed.

### Submit a Puzzle (Web Editor)

Visit the web editor at https://YOURUSERNAME.github.io/REPONAME/ to fill the grid visually.

### How to Submit Manually
1. Fork
2. Edit puzzle/current.txt (9×9, . = empty)
3. Commit & PR to main
4. Wait ~1 min → auto-merge → solution appears

---

   ~~~~~ Wubba Lubba Dub Dub ~~~~~ [burp] ~~~~~
   ╔═══════════════════[ Latest Solve Portal ]═══════════════════╗

<!-- SUDOKU-START -->

**Latest Solve** • Solved in 87 ms • Difficulty: 🟠 Hard • Backtracks: 842 • Clues: 29

5 3 . | . 7 . | . . .
6 . . | 1 9 5 | . . .
. 9 8 | . . . | . 6 .
------+-------+------
8 . . | . 6 . | . . 3
4 . . | 8 . 3 | . . 1
7 . . | . 2 . | . . 6
------+-------+------
. 6 . | . . . | 2 8 .
. . . | 4 1 9 | . . 5
. . . | . 8 . | . 7 9

**Original Puzzle**

53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79

Last solved: 2026-02-20T22:53:00Z UTC (commit abc1234)  
View recent solves → ./history/

<!-- SUDOKU-END -->

10. Difficulty Rules

Level   Emoji   Clues condition         Backtracks condition
Easy    🟢      ≥ 36                    AND ≤ 50
Medium  🟡      32–35                   OR 51–500
Hard    🟠      28–31                   OR 501–5000
Expert  🔴      ≤ 27                    OR > 5000

11. Repo Variable

MAX_HISTORY_KEEP  
(fallback: 50)  
→ max number of history/*.md files retained

12. GitHub Pages Front-end (site/ folder)

A simple static page hosted on GitHub Pages provides a visual 9×9 grid editor.

Purpose: Let users fill the puzzle with mouse/keyboard instead of editing raw text.

Features (minimal version):
- 9×9 grid of single-character input fields
- Visual 3×3 block borders
- Basic validation (only 1-9 or . allowed)
- Submit button → opens GitHub "new file" / "edit file" page with pre-filled puzzle text
- Optional: preview of the 9-line text before submit

Basic implementation outline:

index.html contains <div id="grid"></div> and a Submit button  
script.js dynamically creates 81 <input maxlength="1"> elements  
on submit: read all inputs → build 9-line string → construct URL  
window.open("https://github.com/USER/REPO/new/main?filename=puzzle/current.txt&content=" + encodedPuzzleText)

CSS adds grid layout, thick borders every 3 cells, centered page, mobile-friendly input size.

Deployment: Pages builds from /site folder on main branch → site is live at https://YOURUSERNAME.github.io/REPONAME/

This front-end is completely static → no server, no build step required beyond plain files.

13. Acceptance Criteria Checklist

Puzzle-only PR → auto-approved + auto-merged  
Merge → solver runs → README updated  
New history/*.md created (for valid solutions only), old ones pruned  
Invalid/unsolvable/malformed → error entry in README, no history file created
Grids aligned in monospace  
Separator renders correctly  
Web editor opens GitHub pre-filled PR creation page with correct puzzle text

14. Testing

Goal: Add very basic automated testing that is fast, low-maintenance, and not brittle.

Focus areas:
- Solver correctness (known puzzles solve → correct solution, clues count, difficulty bucket)
- Front-end core flow (grid fills, input validation, submit generates correct puzzle string and opens GitHub PR URL)

Tools:
- Python unittest (built-in, zero deps) for solver.py → run manually only
- Cypress.io (minimal setup) for front-end E2E (grid editor + submit button) → run in CI

Folder structure additions:

tests/
  └── test_solver.py          # Python unit tests for solver (manual only)

cypress/
  ├── e2e/
  │   └── submit.cy.js        # Cypress specs for web editor
  └── support/

Root:
  ├── cypress.config.js       # Cypress config
  └── package.json            # Node.js dependencies

Testing strategy:
- Keep total tests small (5–10 total)
- Test happy path + one failure case only
- Avoid testing layout, timestamps, or GitHub API side-effects
- Python tests: run locally only (python -m unittest discover tests)
- Cypress tests: run in CI on every push/PR via GitHub Actions (fast feedback)
- No Cypress Dashboard or advanced plugins → local + CI only

Example Python unit tests (tests/test_solver.py):

import unittest
from solver import parse_grid, solve_sudoku, count_clues  # assume functions are importable

class TestSolver(unittest.TestCase):
    def test_known_easy_puzzle(self):
        input_str = """53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79"""
        grid = parse_grid(input_str)
        solution, time_ms, backtracks = solve_sudoku(grid)
        self.assertIsNotNone(solution)
        self.assertEqual(count_clues(grid), 29)

    def test_unsolvable(self):
        bad = parse_grid("1" * 81)
        solution, _, _ = solve_sudoku(bad)
        self.assertIsNone(solution)

    def test_difficulty_easy(self):
        # mock or use real low-backtrack puzzle
        pass

Example Cypress test (cypress/e2e/submit.cy.js):

describe('Sudoku Web Editor', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('shows 81 input cells', () => {
    cy.get('input').should('have.length', 81)
  })

  it('rejects invalid input', () => {
    cy.get('input').first().type('a').should('have.value', '')
    cy.get('input').first().type('5').should('have.value', '5')
  })

  it('submit opens GitHub with pre-filled puzzle', () => {
    cy.get('input').eq(0).type('5')
    cy.get('input').eq(1).type('3')
    // ... fill a few more if desired

    cy.window().then(win => {
      cy.stub(win, 'open').as('open')
    })

    cy.get('#submit').click()

    cy.get('@open').should('have.been.calledOnce')
    cy.get('@open').should('have.been.calledWithMatch', /github\.com.*new\/main.*puzzle\/current\.txt.*content=.*53/)
  })
})

CI integration (add to solve-sudoku.yml):

- name: Install Cypress & dependencies
  run: npm ci

- name: Run Cypress tests
  uses: cypress-io/github-action@v6
  with:
    browser: chrome
    start: python -m http.server 8000 --directory site
    wait-on: 'http://localhost:8000'

Note: Python unit tests are NOT run in CI. Run locally with:
  python -m unittest discover tests

Maintenance notes:
- Do not test visual details (colors, exact positions)
- Do not mock GitHub API responses (just verify URL pattern)
- Add more tests only when real bugs appear
- Cypress runs in headless mode in CI → fast & reliable

Wubba lubba dub dub! 🚀
