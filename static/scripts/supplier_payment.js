document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("supplierTable");

    table.addEventListener("click", function (event) {
        const target = event.target;
        const row = target.closest("tr");
        const paymentId = row.dataset.paymentId;

        if (target.classList.contains("edit-btn")) {
            toggleEditMode(row);
        } else if (target.classList.contains("delete-btn")) {
            if (confirm(`هل أنت متأكد من حذف عملية الدفع رقم ${paymentId}؟`)) {
                deleteRecord(paymentId);
            }
        } else if (target.classList.contains("save-btn")) {
            toggleEditMode(row);
        } else if (target.classList.contains("cancel-btn")) {
            cancelEditMode(row);
        }
    });

    function toggleEditMode(row) {
        if (row.classList.contains("edit-mode")) {
            const updatedData = {};
            row.querySelectorAll("td[data-field]").forEach(cell => {
                const input = cell.querySelector("input, select");
                updatedData[cell.dataset.field] = input.value;
            });
            updatedData.id = row.dataset.paymentId;
            updateRecord(updatedData);
        } else {
            row.classList.add("edit-mode");
            row.querySelectorAll("td[data-field]").forEach(cell => {
                const originalValue = cell.textContent.trim();
                const fieldName = cell.dataset.field;

                if (fieldName === "supplier_name") {
                    let options = suppliersList.map(s =>
                        `<option value="${s.supplier_name}" ${originalValue === s.supplier_name ? "selected" : ""}>
                            ${s.supplier_name}
                        </option>`
                    ).join("");
                    cell.innerHTML = `<select name="supplier_name" data-original-value="${originalValue}">${options}</select>`;
                } else if (fieldName === "payment_method") {
                    let options = banksList.map(b =>
                        `<option value="${b.bank_id}" ${originalValue === b.bank_name ? "selected" : ""}>
                            ${b.bank_name}
                        </option>`
                    ).join("");
                    cell.innerHTML = `<select name="payment_method" data-original-value="${originalValue}">${options}</select>`;
                } else if (fieldName === "date_id") {
                    cell.innerHTML = `<input type="date" value="${originalValue.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3')}" data-original-value="${originalValue}">`;
                } else if (fieldName === "notes") {
                    cell.innerHTML = `<input type="text" value="${originalValue}" data-original-value="${originalValue}">`;
                } else {
                    cell.innerHTML = `<input type="number" value="${originalValue}" data-original-value="${originalValue}">`;
                }
            });

            row.querySelector(".actions-cell").innerHTML = `
                <button type="button" class="save-btn">💾</button>
                <button type="button" class="cancel-btn">✖</button>
            `;
        }
    }

    function cancelEditMode(row) {
        row.classList.remove("edit-mode");
        row.querySelectorAll("td[data-field]").forEach(cell => {
            const selectOrInput = cell.querySelector("input, select");
            if (selectOrInput) {
                const originalValue = selectOrInput.dataset.originalValue;
                cell.textContent = originalValue;
            }
        });
        row.querySelector(".actions-cell").innerHTML = `
            <button type="button" class="edit-btn">Edit</button>
            <button type="button" class="delete-btn">Delete</button>
        `;
    }

    function updateRecord(data) {
        console.log("Updating record with data:", data);

        fetch('/update_supplier_payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            console.log("Update response:", result);
            if (result.success) {
                window.location.reload();
            } else {
                alert("خطأ في التحديث: " + result.error);
            }
        })
        .catch(err => {
            console.error("Fetch error:", err);
        });
    }

    function deleteRecord(id) {
        fetch('/delete_supplier_payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        })
            .then(res => res.json())
            .then(result => {
                if (result.success) {
                    window.location.reload();
                } else {
                    alert("خطأ في الحذف: " + result.error);
                }
            })
            .catch(err => console.error(err));
    }
});
