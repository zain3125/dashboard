document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("truckOwnerTable");

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
        // منع تفعيل التعديل على أكثر من صف
        if (document.querySelector("tr.edit-mode") && !row.classList.contains("edit-mode")) {
            alert("أنهاء تعديل الصف الحالي أولاً");
            return;
        }

        if (row.classList.contains("edit-mode")) {
            // حفظ التعديلات
            const updatedData = {};
            row.querySelectorAll("td[data-field]").forEach(cell => {
                const input = cell.querySelector("input, select");
                updatedData[cell.dataset.field] = input.value;
            });
            updatedData.id = row.dataset.paymentId;
            updateRecord(updatedData);
        } else {
            // تفعيل وضع التعديل
            row.classList.add("edit-mode");
            row.querySelectorAll("td[data-field]").forEach(cell => {
                const originalValue = cell.textContent.trim();
                const fieldName = cell.dataset.field;

                if (fieldName === "owner_name") {
                    // هنا يمكن إضافة قائمة منسدلة لمالكي الشاحنات إذا لزم الأمر
                    // حاليًا، يتم التعامل معها كنص فقط
                    cell.innerHTML = `<input type="text" value="${originalValue}" data-original-value="${originalValue}" disabled>`;
                } else {
                    cell.innerHTML = `<input type="text" value="${originalValue}" data-original-value="${originalValue}">`;
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
            const originalValue = cell.querySelector("input").dataset.originalValue;
            cell.textContent = originalValue;
        });
        row.querySelector(".actions-cell").innerHTML = `
            <button type="button" class="edit-btn">Edit</button>
            <button type="button" class="delete-btn">Delete</button>
        `;
    }

    function updateRecord(data) {
        fetch('/update_truck_owner_payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
            .then(res => res.json())
            .then(result => {
                if (result.success) {
                    window.location.reload();
                } else {
                    alert("خطأ في التحديث: " + result.error);
                }
            })
            .catch(err => console.error(err));
    }

    function deleteRecord(id) {
        fetch('/delete_truck_owner_payment', {
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