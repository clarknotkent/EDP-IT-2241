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
const searchInput = document.getElementById('search');
const filterPositionInputs = document.querySelectorAll('input[name="filterPosition"]');


function filterTable() {
    const searchValue = searchInput.value.toLowerCase();
    const filterGenderValue = [...filterGenderInputs].find(input => input.checked).value;
    const filterPositionValue = [...filterPositionInputs].find(input => input.checked).value;
    const minAgeValue = minAgeInput.valueAsNumber || 0;

    [...tableBody.rows].forEach(row => {
        const fullName = row.cells[0].textContent.toLowerCase();
        const gender = row.cells[1].textContent.toLowerCase();
        const age = parseInt(row.cells[2].textContent);

        const showRow = fullName.includes(searchValue)
            && (filterGenderValue === 'all' || gender === filterGenderValue)
            && (filterPositionValue === 'all' || row.cells[3].textContent.toLowerCase() === filterPositionValue)
            && age >= minAgeValue;

        row.style.display = showRow ? '' : 'none';
    });
}

searchInput.addEventListener('input', filterTable);
filterGenderInputs.forEach(input => input.addEventListener('change', filterTable));
filterPositionInputs.forEach(input => input.addEventListener('change', filterTable));
minAgeInput.addEventListener('input', filterTable);
