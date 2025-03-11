document.addEventListener('DOMContentLoaded', function() {
    console.log('Organization JS loaded');

    // Add Organization Form toggling
    const showAddOrganizationFormButton = document.getElementById('showAddOrganizationForm');
    const addOrganizationFormContainer = document.getElementById('addOrganizationFormContainer');
    const cancelAddOrganizationButton = document.getElementById('cancelAddOrganization');
    const editOrganizationFormContainer = document.getElementById('editOrganizationFormContainer');
    const cancelEditOrganizationButton = document.getElementById('cancelEditOrganization');
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    if (showAddOrganizationFormButton && addOrganizationFormContainer && cancelAddOrganizationButton) {
        showAddOrganizationFormButton.addEventListener('click', function() {
            addOrganizationFormContainer.style.display = 'block';
            overlay.style.display = 'block';
        });
        cancelAddOrganizationButton.addEventListener('click', function() {
            addOrganizationFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
        overlay.addEventListener('click', function() {
            addOrganizationFormContainer.style.display = 'none';
            editOrganizationFormContainer.style.display = 'none';
            overlay.style.display = 'none';
        });
    } else {
        console.error("Missing add organization elements");
    }

    // Edit Organization Form handling
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const organizationId = this.getAttribute('data-id');
            const username = this.getAttribute('data-username');
            const email = this.getAttribute('data-email');
            const contact = this.getAttribute('data-contact');
            const category = this.getAttribute('data-category');
            const location = this.getAttribute('data-location');

            document.getElementById('edit_organization_id').value = organizationId;
            document.getElementById('edit_username').value = username;
            document.getElementById('edit_email').value = email;
            document.getElementById('edit_contact').value = contact;
            document.getElementById('edit_category').value = category;
            document.getElementById('edit_location').value = location;

            document.getElementById('editOrganizationForm').action = `/organization/edit_organization/${organizationId}`;

            editOrganizationFormContainer.style.display = 'block';
            overlay.style.display = 'block';
        });
    });

    cancelEditOrganizationButton.addEventListener('click', function() {
        editOrganizationFormContainer.style.display = 'none';
        overlay.style.display = 'none';
    });
});