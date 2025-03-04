document.addEventListener('DOMContentLoaded', () => {
    // Modal elements for adding and editing resources
    const resourceModal = document.getElementById('resourceModal');
    const editResourceModal = document.getElementById('editResourceModal');
    const openResourceModal = document.getElementById('openResourceModal');
    const closeResourceModal = document.getElementById('closeResourceModal');
    const closeEditResourceModal = document.getElementById('closeEditResourceModal');
    const editResourceForm = document.getElementById('editResourceForm');
  
    // Show add resource modal
    openResourceModal.addEventListener('click', () => {
      resourceModal.style.display = 'block';
    });
  
    // Hide add resource modal
    closeResourceModal.addEventListener('click', () => {
      resourceModal.style.display = 'none';
    });
  
    // Hide edit resource modal
    closeEditResourceModal.addEventListener('click', () => {
      editResourceModal.style.display = 'none';
    });
  
    // When clicking outside a modal, hide it
    window.addEventListener('click', (event) => {
      if (event.target === resourceModal) {
        resourceModal.style.display = 'none';
      }
      if (event.target === editResourceModal) {
        editResourceModal.style.display = 'none';
      }
    });
  
    // Edit button functionality
    document.querySelectorAll('.edit-btn').forEach(button => {
      button.addEventListener('click', function() {
        // Retrieve resource data from data attributes
        const resourceId = this.getAttribute('data-id');
        const title = this.getAttribute('data-title');
        const type = this.getAttribute('data-type');
        const link = this.getAttribute('data-link');
  
        // Set the values in the edit form fields
        document.getElementById('edit_resource_id').value = resourceId;
        document.getElementById('edit_resource_title').value = title;
        document.getElementById('edit_resource_type').value = type;
        document.getElementById('edit_resource_link').value = link;
  
        // Update the form action to include the resource id
        editResourceForm.action = `/edit_resource/${resourceId}`;
  
        // Display the edit modal
        editResourceModal.style.display = 'block';
      });
    });
  });  