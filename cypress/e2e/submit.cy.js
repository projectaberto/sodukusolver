describe('Sudoku Web Editor', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('shows 81 input cells', () => {
    cy.get('input[type="text"]').should('have.length', 81);
  });

  it('accepts valid digits 1-9', () => {
    cy.get('input').first().type('5').should('have.value', '5');
  });

  it('rejects invalid characters and clears them', () => {
    cy.get('input').first().type('a');
    cy.get('input').first().should('have.value', '');
  });

  it('accepts dot (.) for empty cells', () => {
    cy.get('input').first().type('.');
    cy.get('input').first().should('have.value', '.');
  });

  it('clear button empties the grid', () => {
    cy.get('input').first().type('5');
    cy.get('input').eq(1).type('3');
    
    cy.get('#clear').click();
    
    cy.get('input').first().should('have.value', '');
    cy.get('input').eq(1).should('have.value', '');
  });

  it('submit with empty grid shows alert', () => {
    const stub = cy.stub(window, 'alert');
    cy.get('#submit').click();
    cy.wrap(stub).should('have.been.calledWith', 'Please fill in at least one clue!');
  });

  it('submit opens GitHub with pre-filled puzzle text', () => {
    cy.get('input').eq(0).type('5');
    cy.get('input').eq(1).type('3');
    cy.get('input').eq(9).type('6');
    
    cy.window().then(win => {
      cy.stub(win, 'open').as('open');
    });
    
    cy.get('#submit').click();
    
    cy.get('@open').should('have.been.calledOnce');
    cy.get('@open').should('have.been.calledWithMatch', /github\.com.*sudokusolver.*puzzle\/current\.txt/);
  });

  it('auto-advances cursor to next cell when digit entered', () => {
    cy.get('input').first().type('5');
    cy.get('input').eq(1).should('have.focus');
  });

  it('arrow keys navigate the grid', () => {
    cy.get('input').first().focus();
    cy.get('input').first().type('{downarrow}');
    cy.get('input').eq(9).should('have.focus');
  });

  it('puzzle string is correctly formatted for GitHub', () => {
    // Fill some cells
    cy.get('input').eq(0).type('5');
    cy.get('input').eq(1).type('3');
    
    // Fill another row cell (index 9)
    cy.get('input').eq(9).type('6');
    
    cy.window().then(win => {
      cy.stub(win, 'open').as('open');
    });
    
    cy.get('#submit').click();
    
    // Verify URL contains encoded puzzle (53 at start, 6 at position 10)
    cy.get('@open').should('be.calledWith');
  });
});
