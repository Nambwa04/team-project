document.addEventListener('DOMContentLoaded', function() {
    console.log('Responder JS loaded');

    // Show and hide Add Responder Form
    const addResponderBtn = document.getElementById('showAddResponderForm');
    const addResponderContainer = document.getElementById('addResponderFormContainer');
    const cancelAddResponderBtn = document.getElementById('cancelAddResponder');

    if (!addResponderBtn || !addResponderContainer || !cancelAddResponderBtn) {
        console.error('Missing one or more required elements:', {
            addResponderBtn,
            addResponderContainer,
            cancelAddResponderBtn
        });
        return;
    }

    addResponderBtn.addEventListener('click', function() {
        console.log('Add Responder button clicked');
        addResponderContainer.style.display = 'block';
    });

    cancelAddResponderBtn.addEventListener('click', function() {
        console.log('Cancel Add Responder button clicked');
        addResponderContainer.style.display = 'none';
    });

    // Attach event listener to each edit button
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const responderId = this.getAttribute('data-id');
            const row = this.closest('tr');
            
            document.getElementById('edit_responder_id').value = responderId;
            document.getElementById('edit_Name').value = row.cells[1].textContent;
            document.getElementById('edit_Contact').value = row.cells[2].textContent;
            document.getElementById('edit_Assigned_Area').value = row.cells[3].textContent;
            
            // Show the edit form
            document.getElementById('editResponderFormContainer').style.display = 'block';
            
            // Update the form action to the correct endpoint
            document.getElementById('editResponderForm').action = '/edit_responder/' + responderId;
        });
    });

    document.getElementById('cancelEditResponder').addEventListener('click', function() {
        document.getElementById('editResponderFormContainer').style.display = 'none';
    });
;
});