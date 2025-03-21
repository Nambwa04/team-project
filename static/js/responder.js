document.addEventListener('DOMContentLoaded', function() {
    console.log('Responder JS loaded');

    // Add Responder Form toggling
    const showAddResponderFormButton = document.getElementById('showAddResponderForm');
    const addResponderFormContainer = document.getElementById('addResponderFormContainer');
    const cancelAddResponderButton = document.getElementById('cancelAddResponder');
    const editResponderFormContainer = document.getElementById('editResponderFormContainer');
    const cancelEditResponderButton = document.getElementById('cancelEditResponder');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    if (showAddResponderFormButton && addResponderFormContainer && cancelAddResponderButton) {
        showAddResponderFormButton.addEventListener('click', function() {
            addResponderFormContainer.style.display = 'block';
            overlay.style.display = 'block';
        });
        cancelAddResponderButton.addEventListener('click', function() {
            addResponderFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
        overlay.addEventListener('click', function() {
            addResponderFormContainer.style.display = 'none';
            editResponderFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
    } else {
        console.error("Missing add responder elements");
    }

    // Edit Responder Form handling
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const responderId = this.getAttribute('data-id');
            const name = this.getAttribute('data-name');
            const contact = this.getAttribute('data-contact');
            const assignedArea = this.getAttribute('data-assigned_area');

            document.getElementById('edit_responder_id').value = responderId;
            document.getElementById('edit_name').value = name;
            document.getElementById('edit_contact').value = contact;
            document.getElementById('edit_assigned_area').value = assignedArea;

            document.getElementById('editResponderForm').action = `/responder/edit_responder/${responderId}`;

            editResponderFormContainer.style.display = 'block';
            overlay.style.display = 'block';
        });
    });

    cancelEditResponderButton.addEventListener('click', function() {
        editResponderFormContainer.style.display = 'none';
        overlay.style.display = 'none';
    });
});