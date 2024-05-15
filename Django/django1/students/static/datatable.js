// Get the form and table references
const form = document.getElementById('myForm');
const tableBody = document.getElementById('tableBody');

// Handle form submission
form.addEventListener('submit', (event) => {
    event.preventDefault();

    // Get the form values
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const age = document.getElementById('age').value;
    const position = document.getElementById('position').value;

    // Create a new table row
    const newRow = document.createElement('tr');

    // Add the data cells to the row
    const fullNameCell = document.createElement('td');
    fullNameCell.textContent = firstName + ' ' + lastName;
    newRow.appendChild(fullNameCell);

    const genderCell = document.createElement('td');
    genderCell.textContent = gender;
    newRow.appendChild(genderCell);

    const ageCell = document.createElement('td');
    ageCell.textContent = age;
    newRow.appendChild(ageCell);

    const positionCell = document.createElement('td');
    positionCell.textContent = position;
    newRow.appendChild(positionCell);

    // Append the new row to the table body
    tableBody.appendChild(newRow);

    // Reset the form
    form.reset();
});

// Handle search/filter changes
const searchInput = document.getElementById('search');
const filterGenderInputs = document.querySelectorAll('input[name="filterGender"]');
const filterPositionInputs = document.querySelectorAll('input[name="filterPosition"]');
const minAgeInput = document.getElementById('minAge');

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
