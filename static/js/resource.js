document.addEventListener('DOMContentLoaded', function() {
    console.log('Resource JS loaded');

    // Add Resource Form toggling
    const showAddResourceFormButton = document.getElementById('showAddResourceForm');
    const addResourceFormContainer = document.getElementById('addResourceFormContainer');
    const cancelAddResourceButton = document.getElementById('cancelAddResource');
    const editResourceFormContainer = document.getElementById('editResourceFormContainer');
    const cancelEditResourceButton = document.getElementById('cancelEditResource');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    if (showAddResourceFormButton && addResourceFormContainer && cancelAddResourceButton) {
        showAddResourceFormButton.addEventListener('click', function() {
            addResourceFormContainer.style.display = 'block';
            overlay.style.display = 'block';
        });
        cancelAddResourceButton.addEventListener('click', function() {
            addResourceFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
        overlay.addEventListener('click', function() {
            addResourceFormContainer.style.display = 'none';
            editResourceFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
    } else {
        console.error("Missing add resource elements");
    }

    // Edit Resource Form handling
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const resourceId = this.getAttribute('data-id');
            const title = this.getAttribute('data-title');
            const type = this.getAttribute('data-type');
            const link = this.getAttribute('data-link');

            document.getElementById('edit_resource_id').value = resourceId;
            document.getElementById('edit_title').value = title;
            document.getElementById('edit_type').value = type;
            document.getElementById('edit_link').value = link;

            document.getElementById('editResourceForm').action = `/resource/edit_resource/${resourceId}`;

            editResourceFormContainer.style.display = 'block';
            overlay.style.display = 'block';
        });
    });

    cancelEditResourceButton.addEventListener('click', function() {
        editResourceFormContainer.style.display = 'none';
        overlay.style.display = 'none';
    });
});