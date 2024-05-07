// Get the form and table references
const form = document.getElementById('myForm');
const tableBody = document.getElementById('tableBody');
    
// Handle form submission
form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent form submission

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
    const snameCell = document.createElement('td');
    const finalCell = document.createElement('td');
    const gtypeCell = document.createElement('td');
    const ylvlCell = document.createElement('td');
    const astatusCell = document.createElement('td');
    const yentryCell = document.createElement('td');
    const elvlCell = document.createElement('td');

    codeCell.textContent = code;
    snameCell.textContent = sname;
    finalCell.textContent = final;
    gtypeCell.textContent = gtype;
    ylvlCell.textContent = ylvl;
    astatusCell.textContent = astatus;
    yentryCell.textContent = yentry;
    elvlCell.textContent = elvl;

    newRow.appendChild(codeCell);
    newRow.appendChild(snameCell);
    newRow.appendChild(finalCell);
    newRow.appendChild(gtypeCell);
    newRow.appendChild(ylvlCell);
    newRow.appendChild(astatusCell);
    newRow.appendChild(yentryCell);
    newRow.appendChild(elvlCell);

    // Append the new row to the table body
    tableBody.appendChild(newRow);

    // Clear the form inputs
    form.reset();
});

// const searchInputs = document.querySelectorAll('');
// searchInputs.forEach(input => input.addEventListener('input', filterStudents));

// function filterStudents() {
//         const searchCode = document.getElementById('search-code').value.toLowerCase();
//         const searchName = document.getElementById('search-name').value.toLowerCase();
//         const searchFinal = document.getElementById('search-final').value.toLowerCase();
//         const searchGradeType = document.getElementById('search-grade-type').value.toLowerCase();
//         const searchYearLevel = document.getElementById('search-year-level').value.toLowerCase();
//         const searchAcadStatus = document.getElementById('search-acad-status').value.toLowerCase();
//         const searchYearOfEntry = document.getElementById('search-year-of-entry').value.toLowerCase();
//         const searchEntryYearLevel = document.getElementById('search-entry-year-level').value.toLowerCase();

//         const tableRows = document.querySelectorAll('');

//         tableRows.forEach(row => {
//             const codeCell = row.cells[0].textContent.toLowerCase();
//             const nameCell = row.cells[1].textContent.toLowerCase();
//             const finalCell = row.cells[2].textContent.toLowerCase();
//             const gradeTypeCell = row.cells[3].textContent.toLowerCase();
//             const yearLevelCell = row.cells[4].textContent.toLowerCase();
//             const acadStatusCell = row.cells[5].textContent.toLowerCase();
//             const yearOfEntryCell = row.cells[6].textContent.toLowerCase();
//             const entryYearLevelCell = row.cells[7].textContent.toLowerCase();

//             const showRow = codeCell.includes(searchCode) &&
//                             nameCell.includes(searchName) &&
//                             finalCell.includes(searchFinal) &&
//                             gradeTypeCell.includes(searchGradeType) &&
//                             yearLevelCell.includes(searchYearLevel) &&
//                             acadStatusCell.includes(searchAcadStatus) &&
//                             yearOfEntryCell.includes(searchYearOfEntry) &&
//                             entryYearLevelCell.includes(searchEntryYearLevel);

//             row.style.display = showRow ? '' : 'none';
//         });
// }
