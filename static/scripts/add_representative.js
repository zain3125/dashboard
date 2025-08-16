document.addEventListener("DOMContentLoaded", function() {
  const table = document.getElementById("representativeTable");

  table.addEventListener("click", function(event) {
    const target = event.target;
    const row = target.closest("tr");
    const originalRepresentativeId = row.dataset.representativeId;

    if (target.classList.contains("edit-btn")) {
      toggleEditMode(row);
    } else if (target.classList.contains("delete-btn")) {
      const originalRepresentativeName = row.dataset.representativeName;
      if (confirm(`هل أنت متأكد من حذف المندوب الذي اسمه '${originalRepresentativeName}'؟`)) {
        deleteRecord(originalRepresentativeName, '/delete_representative');
      }
    } else if (target.classList.contains("save-btn")) {
        const newRepresentativeName = row.querySelector('td[data-field="representative_name"] input').value;
        const newPhone = row.querySelector('td[data-field="phone"] input').value;
        
        // أضف هذا المتغير الجديد
        const originalRepresentativeName = row.dataset.representativeName; 

        // عدّل الدالة لترسل البيانات الجديدة بالإضافة إلى الاسم الأصلي
        updateRecord({
            id: originalRepresentativeId,
            original_representative_name: originalRepresentativeName, // الاسم الأصلي
            new_representative_name: newRepresentativeName, // الاسم الجديد
            phone: newPhone
        }, '/update_representative');
    } else if (target.classList.contains("cancel-btn")) {
      toggleEditMode(row);
    }
  });

  function toggleEditMode(row) {
    row.classList.toggle("edit-mode");
    const isEditMode = row.classList.contains("edit-mode");
    
    row.querySelectorAll("td[data-field]").forEach(cell => {
      const fieldName = cell.dataset.field;
      if (isEditMode) {
        const originalValue = cell.textContent.trim();
        cell.innerHTML = `<input type="text" value="${originalValue}" data-original-value="${originalValue}" name="${fieldName}">`;
      } else {
        const originalValue = cell.querySelector("input").dataset.originalValue;
        cell.textContent = originalValue;
      }
    });

    const actionsCell = row.querySelector(".actions-cell");
    if (isEditMode) {
      actionsCell.innerHTML = `
        <button type="button" class="save-btn">Save</button>
        <button type="button" class="cancel-btn">Cancel</button>
      `;
    } else {
      actionsCell.innerHTML = `
        <button type="button" class="edit-btn">Edit</button>
        <button type="button" class="delete-btn">Delete</button>
      `;
    }
  }

  function updateRecord(data, url) {
    fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }, // هذا السطر هو الأهم!
          body: JSON.stringify(data),
        })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        window.location.reload();
      } else {
        alert('حدث خطأ في التحديث: ' + result.error);
      }
    })
    .catch(error => console.error('Error:', error));
  }
  function deleteRecord(name, url) {
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ representative_name: name }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        return response.json();
    })
    .then(result => {
      if (result.success) {
        window.location.reload();
      } else {
        alert('حدث خطأ في الحذف: ' + result.error);
      }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('فشل الاتصال بالخادم: ' + error.message);
    });
  }
});