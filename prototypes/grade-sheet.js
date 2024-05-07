// Get the form and table references
const form = document.getElementById('myForm');
const tableBody = document.getElementById('tableBody');

// Handle form submission
form.addEventListener('submit', (event) => {
    event.preventDefault();

    // Get the form values
    const code = document.getElementById('code').value;
    const sname = document.getElementById('sname').value; 
    const final = document.getElementById('final').value;
    const gtype = document.getElementById('gtype').value; 
    const ylvl = document.getElementById('ylvl').value; 
    const astatus = document.getElementById('astatus').value; 
    const yentry = document.getElementById('yentry').value;
    const elvl = document.getElementById('elvl').value;
    
    // Create a new table row
    const newRow = document.createElement('tr');

    // Add the data cells to the row
    const codeCell = document.createElement('td');
    codeCell.textContent = code;
    newRow.appendChild(codeCell);

    const snameCell = document.createElement('td');
    snameCell.textContent = sname;
    newRow.appendChild(snameCell);

    const finalCell = document.createElement('td');
    finalCell.textContent = final;
    newRow.appendChild(finalCell);

    const gtypeCell = document.createElement('td');
    gtypeCell.textContent = gtype;
    newRow.appendChild(gtypeCell);

    const ylvlCell = document.createElement('td');
    ylvlCell.textContent = ylvl;
    newRow.appendChild(ylvlCell);

    const astatusCell = document.createElement('td');
    astatusCell.textContent = astatus;
    newRow.appendChild(astatusCell);

    const yentryCell = document.createElement('td');
    yentryCell.textContent = yentry;
    newRow.appendChild(yentryCell);

    const elvlCell = document.createElement('td');
    elvlCell.textContent = elvl;
    newRow.appendChild(elvlCell);

    // Append the new row to the table body
    tableBody.appendChild(newRow);

    // Reset the form
    form.reset();
});

// Handle search/filter changes
//
// Column order in #myTable:
//   0 CODE | 1 STUDENT NAME | 2 FINAL | 3 GRD. TYPE
//   4 YEAR LVL | 5 ACAD. STATUS | 6 YR. OF ENTRY | 7 ENTRY YR. LVL
const searchInput = document.getElementById('search');
const filterGradeTypeInputs = document.querySelectorAll('input[name="filterGradeType"]');
const filterStatusInputs = document.querySelectorAll('input[name="filterStatus"]');
const filterYearLevelSelect = document.getElementById('filterYearLevel');

function checkedValue(inputs) {
    const checked = [...inputs].find(input => input.checked);
    return checked ? checked.value : 'all';
}

function filterTable() {
    const searchValue = searchInput.value.trim().toLowerCase();
    const gradeTypeValue = checkedValue(filterGradeTypeInputs);
    const statusValue = checkedValue(filterStatusInputs);
    const yearLevelValue = filterYearLevelSelect.value;

    [...tableBody.rows].forEach(row => {
        const studentName = row.cells[1].textContent.toLowerCase();
        const gradeType = row.cells[3].textContent.trim().toLowerCase();
        const yearLevel = row.cells[4].textContent.trim();
        const acadStatus = row.cells[5].textContent.trim().toLowerCase();

        const showRow = studentName.includes(searchValue)
            && (gradeTypeValue === 'all' || gradeType === gradeTypeValue)
            && (statusValue === 'all' || acadStatus === statusValue)
            && (yearLevelValue === 'all' || yearLevel === yearLevelValue);

        row.style.display = showRow ? '' : 'none';
    });
}

searchInput.addEventListener('input', filterTable);
filterGradeTypeInputs.forEach(input => input.addEventListener('change', filterTable));
filterStatusInputs.forEach(input => input.addEventListener('change', filterTable));
filterYearLevelSelect.addEventListener('change', filterTable);
