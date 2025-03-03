document.addEventListener('DOMContentLoaded', function() {
    console.log('Victim JS loaded');

    // Add Victim Form toggling
    const addVictimBtn = document.getElementById('showAddVictimForm');
    const addVictimContainer = document.getElementById('addVictimFormContainer');
    const cancelAddVictimBtn = document.getElementById('cancelAddVictim');

    if (addVictimBtn && addVictimContainer && cancelAddVictimBtn) {
        addVictimBtn.addEventListener('click', function() {
            addVictimContainer.style.display = 'block';
        });
        cancelAddVictimBtn.addEventListener('click', function() {
            addVictimContainer.style.display = 'none';
        });
    } else {
        console.error("Missing add victim elements");
    }

    // Edit Victim Form handling
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const victimId = this.getAttribute('data-id');
            const row = this.closest('tr');
        
            document.getElementById('edit_victim_id').value = victimId;
            document.getElementById('edit_name').value = row.cells[1].textContent;
            document.getElementById('edit_gender').value = row.cells[2].textContent;
            document.getElementById('edit_location').value = row.cells[3].textContent;
            document.getElementById('editVictimFormContainer').style.display = 'block';
            document.getElementById('editVictimForm').action = '/edit_victim/' + victimId;
        });
    });

    document.getElementById('cancelEditVictim').addEventListener('click', function() {
        document.getElementById('editVictimFormContainer').style.display = 'none';
    });
});