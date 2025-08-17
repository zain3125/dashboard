document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.querySelector("#data-table tbody");
    
    // Check if the variables from Jinja are available
    if (typeof truckArr === 'undefined' || typeof suppliers === 'undefined' || typeof factories === 'undefined' || typeof zones === 'undefined' || typeof representatives === 'undefined') {
        console.error("Jinja variables are not defined. Make sure the script is loaded after the variables in the HTML file.");
        return;
    }

    // Event listener for truck number changes to update owner
    tbody.addEventListener('change', function(e) {
        const sel = e.target;
        if (sel && sel.matches('select[name="truck_num[]"]')) {
            const row = sel.closest('tr');
            const ownerInput = row.querySelector('input[name="truck_owner[]"]');
            const owner = truckMap[sel.value] || '';
            if (ownerInput) ownerInput.value = owner;
        }
    });

    // Event listener for removing a row
    tbody.addEventListener('click', function(e) {
        const btn = e.target;
        if (btn && btn.matches('.remove-row')) {
            const row = btn.closest('tr');
            const rows = tbody.querySelectorAll('tr');
            if (rows.length > 1) {
                row.remove();
            } else {
                row.querySelectorAll('input, select').forEach(el => {
                    if (el.tagName === 'SELECT') el.selectedIndex = 0;
                    else el.value = '';
                });
            }
        }
    });

    // Function to add a new row to the table
    window.addRow = function() {
        const firstRow = tbody.rows[0];
        const newRow = firstRow.cloneNode(true);

        // clear the values in the new row
        newRow.querySelectorAll('input, select').forEach(el => {
            if (el.tagName === 'SELECT') el.selectedIndex = 0;
            else el.value = '';
        });

        // The representative select field in the cloned row should have an array name
        const repSelect = newRow.querySelector('select[name="representative[]"]');
        if (repSelect) {
            repSelect.name = 'representative[]';
        }

        tbody.appendChild(newRow);
    }

    // Event listener for edit/save buttons
    document.addEventListener('click', function(e) {
        // Edit mode
        if (e.target.classList.contains('edit-btn')) {
            const row = e.target.closest('tr');
            const cells = row.querySelectorAll('td');

            const columnNames = ["date", "truck_num", "truck_owner", "supplier", "factory", "zone", "weight", "ohda", "factory_price", "sell_price", "representative"];
            
            cells.forEach((cell, idx) => {
                if (idx < 11) { // 11 columns for data
                    const value = cell.innerText.trim();
                    let newContent;

                    switch(columnNames[idx]) {
                        case "date":
                            newContent = `<input type="date" name="date[]" class="border rounded px-1 w-full" value="${value}">`;
                            break;
                        case "truck_num":
                            newContent = `<select name="truck_num[]" class="border rounded px-1 w-full">
                                <option value="">Select Truck</option>
                                ${truckArr.map(pair => `<option value="${pair[0]}" ${String(pair[0]) === value ? 'selected' : ''}>${pair[0]}</option>`).join('')}
                            </select>`;
                            break;
                        case "supplier":
                            newContent = `<select name="supplier[]" class="border rounded px-1 w-full">
                                <option value="">Select Supplier</option>
                                ${suppliers.map(sup => `<option value="${sup.supplier_name}" ${sup.supplier_name === value ? 'selected' : ''}>${sup.supplier_name}</option>`).join('')}
                            </select>`;
                            break;
                        case "factory":
                            // Corrected mapping for factories
                            newContent = `<select name="factory[]" class="border rounded px-1 w-full">
                                <option value="">Select Factory</option>
                                ${factories.map(fac => `<option value="${fac.factory_name}" ${fac.factory_name === value ? 'selected' : ''}>${fac.factory_name}</option>`).join('')}
                            </select>`;
                            break;
                        case "zone":
                            // Corrected mapping for zones
                            newContent = `<select name="zone[]" class="border rounded px-1 w-full">
                                <option value="">Select Zone</option>
                                ${zones.map(z => `<option value="${z.zone_name}" ${z.zone_name === value ? 'selected' : ''}>${z.zone_name}</option>`).join('')}
                            </select>`;
                            break;
                        case "representative":
                            newContent = `<select name="representative[]" class="border rounded px-1 w-full">
                                <option value="">Select Representative</option>
                                ${representatives.map(rep => 
                                    `<option value="${rep.representative_name}" ${rep.representative_name === value ? 'selected' : ''}>${rep.representative_name}</option>`
                                ).join('')}
                            </select>`;
                            break;
                        case "truck_owner":
                            newContent = `<input type="text" name="truck_owner[]" class="border rounded px-1 w-full bg-gray-100" value="${value}" readonly>`;
                            break;
                        default:
                            newContent = `<input type="number" name="${columnNames[idx]}[]" step="any" class="border rounded px-1 w-full" value="${value}">`;
                            break;
                    }
                    cell.innerHTML = newContent;
                }
            });

            e.target.classList.add('hidden');
            row.querySelector('.save-btn').classList.remove('hidden');
        }

        // Save mode
        if (e.target.classList.contains('save-btn')) {
            const row = e.target.closest('tr');
            const id = e.target.getAttribute('data-id');
            const cells = row.querySelectorAll('td');
            const data = { id: id };
            
            const columnNames = ["date", "truck_num", "truck_owner", "supplier", "factory", "zone", "weight", "ohda", "factory_price", "sell_price", "representative"];
            
            cells.forEach((cell, idx) => {
                if (idx < 11) {
                    const inputElement = cell.querySelector('input, select');
                    if (inputElement) {
                        data[columnNames[idx]] = inputElement.value;
                        if (inputElement.tagName === 'SELECT') {
                            cell.innerHTML = inputElement.options[inputElement.selectedIndex].text;
                        } else {
                            cell.innerHTML = inputElement.value;
                        }
                    }
                }
            });

            fetch('/update_record', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(res => {
                if (res.success) {
                    e.target.classList.add('hidden');
                    row.querySelector('.edit-btn').classList.remove('hidden');
                } else {
                    alert('Error saving changes.');
                }
            });
        }
    });

    // Modal functions for delete
    window.openModal = function(id) {
        document.getElementById('deleteId').value = id;
        document.getElementById('deleteModal').classList.remove('hidden');
    }
    window.closeModal = function() {
        document.getElementById('deleteModal').classList.add('hidden');
    }
});