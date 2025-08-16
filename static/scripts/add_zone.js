document.addEventListener("DOMContentLoaded", function() {
  const table = document.getElementById("zoneTable");

  table.addEventListener("click", function(event) {
    const target = event.target;
    const row = target.closest("tr");
    if (!row) return; // Make sure the click was inside a row

    const originalZoneName = row.dataset.zoneName;

    if (target.classList.contains("edit-btn")) {
      toggleEditMode(row);
    } else if (target.classList.contains("delete-btn")) {
      if (confirm(`هل أنت متأكد من حذف المنطقة '${originalZoneName}'؟`)) {
        deleteRecord(originalZoneName, '/delete_zone');
      }
    } else if (target.classList.contains("save-btn")) {
      const inputElement = row.querySelector('input[name="zone_name"]');
      const newZoneName = inputElement ? inputElement.value : '';
      if (newZoneName) {
        updateRecord({
          id: originalZoneName,
          zone_name: newZoneName,
        }, '/update_zone');
      } else {
        alert("لا يمكن أن يكون اسم المنطقة فارغًا.");
      }
    } else if (target.classList.contains("cancel-btn")) {
      toggleEditMode(row);
    }
  });

  function toggleEditMode(row) {
    const isEditMode = row.classList.toggle("edit-mode");
    
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(result => {
      if (result.success) {
        window.location.reload();
      } else {
        alert('حدث خطأ في التحديث: ' + (result.error || 'خطأ غير معروف'));
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('حدث خطأ أثناء الاتصال بالخادم.');
    });
  }

  function deleteRecord(name, url) {
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zone_name: name }),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(result => {
      if (result.success) {
        window.location.reload();
      } else {
        alert('حدث خطأ في الحذف: ' + (result.error || 'خطأ غير معروف'));
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('حدث خطأ أثناء الاتصال بالخادم.');
    });
  }
});