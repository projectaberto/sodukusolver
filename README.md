# Sudoku Solver Portal

Public 9×9 Sudoku solver running in GitHub Actions.

Submit puzzles easily via the web editor below or by editing `puzzle/current.txt` → open PR → auto-merges if only that file changed.

## Submit a Puzzle

### Web Editor
Visit the interactive grid editor: https://projectaberto.github.io/sudokusolver/

### Manual Submission
1. Fork the repository
2. Edit `puzzle/current.txt` (9×9 grid, `.` = empty cell)
3. Commit and open a Pull Request to `main`
4. Wait ~1 minute → PR auto-merges → solution appears here

---

   ~~~~~ Wubba Lubba Dub Dub ~~~~~ [burp] ~~~~~
   ╔═══════════════════[ Latest Solve Portal ]═══════════════════╗

<!-- SUDOKU-START -->

No solutions yet. Submit your first puzzle!

<!-- SUDOKU-END -->

---

## How It Works

1. You submit a puzzle (text file or web editor)
2. GitHub Actions automatically solves it
3. Solution is posted here with difficulty rating
4. History of all solved puzzles is archived

## Difficulty Levels

| Level | Emoji | Clues | Backtracks |
|-------|-------|-------|-----------|
| Easy | 🟢 | ≥ 36 | AND ≤ 50 |
| Medium | 🟡 | 32–35 | OR 51–500 |
| Hard | 🟠 | 28–31 | OR 501–5000 |
| Expert | 🔴 | ≤ 27 | OR > 5000 |

## Puzzle Format

Each puzzle is 9 lines, 9 characters per line:
- `1-9`: clue (given number)
- `.`: empty cell
- No spaces, no other characters

Example:
```
53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79
```

## Technology

- **Solver**: Python 3.12 (backtracking algorithm, zero dependencies)
- **Front-end**: Vanilla HTML/CSS/JavaScript (GitHub Pages)
- **Testing**: Python unittest + Cypress.io
- **CI/CD**: GitHub Actions
- **Auto-merge**: PR guard that only merges puzzle-only changes

## Local Development

### Run Solver Tests
```bash
python -m unittest discover tests
```

### Run Front-end Tests
```bash
npm ci
npm run test:e2e
```

### Serve Front-end Locally
```bash
npm run serve
```

Then visit http://localhost:8000

---

Wubba lubba dub dub! 🚀
