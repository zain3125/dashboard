
document.addEventListener("DOMContentLoaded", function() {
    const truckTable = document.getElementById("truckTable");

    // Handle Edit and Delete buttons
    truckTable.addEventListener("click", function(event) {
    const target = event.target;
    const row = target.closest("tr");
    const truckNum = row.dataset.truckNum;
    
    if (target.classList.contains("edit-btn")) {
        toggleEditMode(row);
    } else if (target.classList.contains("delete-btn")) {
        if (confirm(`Are you sure you want to delete truck number ${truckNum}?`)) {
        deleteRecord(truckNum);
        }
    }
    });
    
    function toggleEditMode(row) {
    if (row.classList.contains("edit-mode")) {
        // Save the changes
        const truckNumInput = row.querySelector('td[data-field="truck_num"] input').value;
        const ownerNameInput = row.querySelector('td[data-field="owner_name"] input').value;
        const phoneInput = row.querySelector('td[data-field="phone"] input').value;

        const originalTruckNum = row.dataset.truckNum;

        updateRecord({
        id: originalTruckNum,
        truck_num: truckNumInput,
        owner_name: ownerNameInput,
        phone: phoneInput
        });
    } else {
        // Switch to edit mode
        row.classList.add("edit-mode");
        row.querySelectorAll("td[data-field]").forEach(cell => {
        const originalValue = cell.textContent.trim();
        const fieldName = cell.dataset.field;
        cell.innerHTML = `<input type="text" value="${originalValue}" data-original-value="${originalValue}" name="${fieldName}">`;
        });

        // Change buttons
        const actionsCell = row.querySelector(".actions-cell");
        actionsCell.innerHTML = `
        <button type="button" class="save-btn">Save</button>
        <button type="button" class="cancel-btn">Cancel</button>
        `;
    }
    }

    // Handle Save and Cancel buttons
    truckTable.addEventListener("click", function(event) {
    const target = event.target;
    const row = target.closest("tr");
    
    if (target.classList.contains("save-btn")) {
        // The toggleEditMode function already handles the logic for saving.
        toggleEditMode(row);
    } else if (target.classList.contains("cancel-btn")) {
        row.classList.remove("edit-mode");
        row.querySelectorAll("td[data-field]").forEach(cell => {
        const originalValue = cell.querySelector("input").dataset.originalValue;
        cell.textContent = originalValue;
        });
        const actionsCell = row.querySelector(".actions-cell");
        actionsCell.innerHTML = `
        <button type="button" class="edit-btn">Edit</button>
        <button type="button" class="delete-btn">Delete</button>
        `;
    }
    });

    // Function to send update request to the server
    function updateRecord(data) {
    fetch('/update_truck_owner', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
        window.location.reload(); // Reload to show the updated data
        } else {
        alert('Error updating record: ' + result.error);
        }
    })
    .catch(error => console.error('Error:', error));
    }

    // Function to send delete request to the server
    function deleteRecord(truckNum) {
    fetch('/delete_truck_owner', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({ truck_num: truckNum }),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
        window.location.reload(); // Reload to show the updated data
        } else {
        alert('Error deleting record: ' + result.error);
        }
    })
    .catch(error => console.error('Error:', error));
    }
});
