document.addEventListener("DOMContentLoaded", function () {
    /** MODAL FUNCTIONALITY (ADD RESPONDER) **/
    const modal = document.getElementById("addResponderModal");
    const openModalBtn = document.getElementById("openModal");
    const closeModalBtns = document.querySelectorAll(".close-modal");
    const saveResponderBtn = document.getElementById("saveResponder");

    if (modal) {
        // Open Modal
        openModalBtn?.addEventListener("click", () => modal.style.display = "flex");

        // Close Modal (for close & cancel buttons)
        closeModalBtns.forEach(btn => btn.addEventListener("click", () => modal.style.display = "none"));

        // Save Responder
        saveResponderBtn?.addEventListener("click", function () {
            const name = document.getElementById("responderName").value.trim();
            const contact = document.getElementById("responderContact").value.trim();
            const area = document.getElementById("responderArea").value.trim();
            const table = document.querySelector("#respondersTable tbody");

            if (name && contact && area && table) {
                let newRow = table.insertRow();
                newRow.innerHTML = `
                    <td>${table.rows.length}</td>
                    <td>${name}</td>
                    <td>${contact}</td>
                    <td>${area}</td>
                    <td>
                        <button class="edit-btn">Edit</button>
                        <button class="delete-btn">Delete</button>
                    </td>
                `;

                // Close and Clear Modal
                modal.style.display = "none";
                document.getElementById("responderName").value = "";
                document.getElementById("responderContact").value = "";
                document.getElementById("responderArea").value = "";
            } else {
                alert("Please fill in all fields.");
            }
        });

        // Close modal when clicking outside of it
        window.addEventListener("click", (event) => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    }

    /** PROFILE EDIT MODAL FUNCTIONALITY **/
    const editModal = document.getElementById("editProfileModal");
    const editBtn = document.getElementById("editProfileBtn");
    const closeEditBtn = document.querySelector(".close-edit-modal");
    const editForm = document.getElementById("editProfileForm");

    if (editBtn) {
        editBtn.addEventListener("click", () => editModal.style.display = "flex");
    }

    if (closeEditBtn) {
        closeEditBtn.addEventListener("click", () => editModal.style.display = "none");
    }

    window.addEventListener("click", (event) => {
        if (event.target === editModal) {
            editModal.style.display = "none";
        }
    });

    /** SAVE PROFILE CHANGES **/
    editForm?.addEventListener("submit", function (e) {
        e.preventDefault();

        const newName = document.getElementById("editName").value.trim();
        const newEmail = document.getElementById("editEmail").value.trim();
        const newPhone = document.getElementById("editPhone").value.trim();

        if (newName) document.getElementById("userName").textContent = newName;
        if (newEmail) document.getElementById("userEmail").textContent = newEmail;
        if (newPhone) document.getElementById("userPhone").textContent = newPhone;

        editModal.style.display = "none"; // Close modal
    });

    /** NAVIGATION MENU **/
    const hamburger = document.getElementById("hamburger");
    const navbar = document.getElementById("navbar");

    hamburger?.addEventListener("click", () => navbar.classList.toggle("active"));

    /** FOOTER VISIBILITY **/
    const footer = document.getElementById("footer");

    if (footer) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    footer.style.visibility = entry.isIntersecting ? "visible" : "hidden";
                    footer.style.opacity = entry.isIntersecting ? "1" : "0";
                });
            },
            { threshold: 0.1 } // Footer appears when at least 10% is visible
        );
        observer.observe(footer);
    }

    /** LOGOUT FUNCTIONALITY **/
    const confirmLogoutBtn = document.getElementById("confirmLogout");
    const cancelLogoutBtn = document.getElementById("cancelLogout");

    if (confirmLogoutBtn && cancelLogoutBtn) {
        confirmLogoutBtn.addEventListener("click", function () {
            window.location.href = "frontpage.html"; // Redirect to login page or logout script
        });

        cancelLogoutBtn.addEventListener("click", function () {
            window.history.back();
        });
    }
});
