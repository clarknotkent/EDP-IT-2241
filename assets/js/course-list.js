// Course list — add a curriculum row, and filter the table per column.
//
// This is the script the page was always meant to have. The original submission
// shipped the markup (an add row, a search row, a commented-out tbody) but no
// JS at all; a half-adapted draft of the filter sat commented out at the bottom
// of SubmitGrades.js with empty querySelectorAll('') selectors.
//
// Column order in #tableBody:
//   0 YEAR LEVEL | 1 SEMESTER | 2 SUBJ. NO | 3 DESCRIPTIVE TITLE
//   4 UNITS | 5 GRADE | 6 PREREQUISITE | 7 REMARKS

const FIELDS = ['ylvl', 'sem', 'subno', 'dtitle', 'units', 'grade', 'prereq', 'remarks'];

const tableBody = document.getElementById('tableBody');
const addRowButton = document.getElementById('addRowButton');
const inputs = FIELDS.map(id => document.getElementById(id));
const searchInputs = FIELDS.map(id => document.getElementById(`search-${id}`));

// --- Add a row -------------------------------------------------------------

function addRow() {
    // The first four columns identify the subject; require them.
    const required = inputs.slice(0, 4);
    const missing = required.filter(input => !input.value.trim());
    if (missing.length) {
        missing[0].focus();
        return;
    }

    const row = document.createElement('tr');
    row.className = tableBody.rows.length % 2 === 0 ? 'odd' : 'even';

    inputs.forEach(input => {
        const cell = document.createElement('td');
        cell.textContent = input.value.trim();
        row.appendChild(cell);
    });

    tableBody.appendChild(row);
    inputs.forEach(input => { input.value = ''; });
    inputs[0].focus();

    // A new row should respect whatever filter is currently active.
    filterTable();
}

addRowButton.addEventListener('click', addRow);

// Enter anywhere in the add row submits it, rather than doing nothing.
inputs.forEach(input => {
    input.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            addRow();
        }
    });
});

// --- Filter ----------------------------------------------------------------

function filterTable() {
    const terms = searchInputs.map(input => input.value.trim().toLowerCase());

    [...tableBody.rows].forEach(row => {
        const matches = terms.every((term, index) => {
            if (!term) return true;
            const cell = row.cells[index];
            return cell ? cell.textContent.toLowerCase().includes(term) : false;
        });
        row.style.display = matches ? '' : 'none';
    });
}

searchInputs.forEach(input => input.addEventListener('input', filterTable));
