// Show/hide add form
document.getElementById('showAddForm').addEventListener('click', function() {
    document.getElementById('addOrgFormContainer').style.display = 'block';
});

document.getElementById('cancelAdd').addEventListener('click', function() {
    document.getElementById('addOrgFormContainer').style.display = 'none';
});

// Handle edit button clicks
document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', function() {
        const orgId = this.getAttribute('data-id');
        const row = this.closest('tr');
        
        // Fill the edit form with current values
        document.getElementById('edit_id').value = orgId;
        document.getElementById('edit_name').value = row.cells[1].textContent;
        document.getElementById('edit_contact').value = row.cells[2].textContent;
        document.getElementById('edit_category').value = row.cells[3].textContent;
        document.getElementById('edit_location').value = row.cells[4].textContent;
        
        // Show the edit form
        document.getElementById('editOrgFormContainer').style.display = 'block';
        
        // Update the form action
        document.getElementById('editOrgFormContainer').style.display = 'block';
        document.getElementById('editOrgForm').action = `/organization/${orgId}`;
    });
});

document.getElementById('cancelEdit').addEventListener('click', function() {
    document.getElementById('editOrgFormContainer').style.display = 'none';
});