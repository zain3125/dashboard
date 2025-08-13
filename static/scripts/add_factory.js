document.addEventListener("DOMContentLoaded", function() {
  const table = document.getElementById("factoryTable");

  table.addEventListener("click", function(event) {
    const target = event.target;
    const row = target.closest("tr");
    const originalFactoryName = row.dataset.factoryName;

    if (target.classList.contains("edit-btn")) {
      toggleEditMode(row);
    } else if (target.classList.contains("delete-btn")) {
      if (confirm(`هل أنت متأكد من حذف المصنع '${originalFactoryName}'؟`)) {
        deleteRecord(originalFactoryName, '/delete_factory');
      }
    } else if (target.classList.contains("save-btn")) {
      const newFactoryName = row.querySelector('td[data-field="factory_name"] input').value;
      updateRecord({
        id: originalFactoryName,
        factory_name: newFactoryName,
      }, '/update_factory');
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
      headers: { 'Content-Type': 'application/json' },
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
      body: JSON.stringify({ factory_name: name }),
    })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        window.location.reload();
      } else {
        alert('حدث خطأ في الحذف: ' + result.error);
      }
    })
    .catch(error => console.error('Error:', error));
  }
});