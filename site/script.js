/**
 * Sudoku Web Editor
 * - 9x9 grid with input validation
 * - Submit opens pre-filled GitHub PR creation page
 */

class SudokuEditor {
    constructor() {
        this.gridElement = document.getElementById('grid');
        this.clearButton = document.getElementById('clear');
        this.submitButton = document.getElementById('submit');
        this.inputs = [];
        
        this.initializeGrid();
        this.attachEventListeners();
    }
    
    initializeGrid() {
        // Create 81 input fields
        for (let i = 0; i < 81; i++) {
            const input = document.createElement('input');
            input.type = 'text';
            input.maxLength = 1;
            input.inputMode = 'numeric';
            input.setAttribute('data-index', i);
            
            input.addEventListener('input', (e) => this.handleInput(e));
            input.addEventListener('keydown', (e) => this.handleKeyDown(e));
            
            this.gridElement.appendChild(input);
            this.inputs.push(input);
        }
    }
    
    handleInput(e) {
        const input = e.target;
        let value = input.value.toUpperCase();
        
        // Allow only 1-9 or . or empty
        if (value === '') {
            input.value = '';
        } else if (/^[1-9]$/.test(value)) {
            input.value = value;
            // Auto-advance to next cell
            const index = parseInt(input.getAttribute('data-index'));
            if (index < 80) {
                this.inputs[index + 1].focus();
            }
        } else if (value === '.') {
            input.value = '.';
            const index = parseInt(input.getAttribute('data-index'));
            if (index < 80) {
                this.inputs[index + 1].focus();
            }
        } else {
            // Invalid character - clear it
            input.value = '';
        }
    }
    
    handleKeyDown(e) {
        const input = e.target;
        const index = parseInt(input.getAttribute('data-index'));
        
        // Backspace/Delete - clear and move to previous
        if ((e.key === 'Backspace' || e.key === 'Delete') && input.value === '') {
            e.preventDefault();
            if (index > 0) {
                this.inputs[index - 1].focus();
                this.inputs[index - 1].value = '';
            }
        }
        
        // Space - empty cell marker
        if (e.key === ' ') {
            e.preventDefault();
            input.value = '';
            if (index < 80) {
                this.inputs[index + 1].focus();
            }
        }
        
        // Arrow keys for navigation
        if (e.key === 'ArrowUp' && index >= 9) {
            e.preventDefault();
            this.inputs[index - 9].focus();
        } else if (e.key === 'ArrowDown' && index < 72) {
            e.preventDefault();
            this.inputs[index + 9].focus();
        } else if (e.key === 'ArrowLeft' && index > 0 && index % 9 !== 0) {
            e.preventDefault();
            this.inputs[index - 1].focus();
        } else if (e.key === 'ArrowRight' && index < 80 && (index + 1) % 9 !== 0) {
            e.preventDefault();
            this.inputs[index + 1].focus();
        }
    }
    
    attachEventListeners() {
        this.clearButton.addEventListener('click', () => this.clearGrid());
        this.submitButton.addEventListener('click', () => this.submit());
    }
    
    clearGrid() {
        this.inputs.forEach(input => input.value = '');
        this.inputs[0].focus();
    }
    
    getPuzzleString() {
        let puzzleString = '';
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const index = row * 9 + col;
                const value = this.inputs[index].value;
                puzzleString += (value === '' ? '.' : value);
            }
            if (row < 8) {
                puzzleString += '\n';
            }
        }
        return puzzleString;
    }
    
    getRepoInfo() {
        /**
         * Auto-detect GitHub username and repo from GitHub Pages URL.
         * Format: https://USERNAME.github.io/REPONAME/
         */
        const url = window.location.href;
        const match = url.match(/https:\/\/([^.]+)\.github\.io\/([^\/]+)\//);
        
        if (match) {
            return {
                username: match[1],
                repo: match[2]
            };
        }
        
        // Fallback for local testing
        return {
            username: 'projectaberto',
            repo: 'sudokusolver'
        };
    }
    
    submit() {
        const puzzle = this.getPuzzleString();
        const repo = this.getRepoInfo();
        
        // Validate puzzle is not empty
        const filledCells = puzzle.replace(/\n|\./g, '').length;
        if (filledCells === 0) {
            alert('Please fill in at least one clue!');
            return;
        }
        
        // Build GitHub URL for creating a new PR
        // Pattern: GitHub allows pre-filling file edits with query parameters
        const githubUrl = new URL(
            `https://github.com/${repo.username}/${repo.repo}/new/main`
        );
        
        githubUrl.searchParams.set('filename', 'puzzle/current.txt');
        githubUrl.searchParams.set('value', puzzle);
        
        // Open in new tab
        window.open(githubUrl.toString(), '_blank');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new SudokuEditor();
});
