// Sidebar Menu Toggle Logic

if (toggle && sidebar && content) {
    // Toggle sidebar open/close on click
    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("active"); // Toggle sidebar "active" state
        content.classList.toggle("active"); // Adjust content width accordingly

        // Save sidebar state in localStorage
        localStorage.setItem("sidebarState", sidebar.classList.contains("active") ? "active" : "");
    });

    // Restore sidebar state from localStorage on page load
    document.addEventListener("DOMContentLoaded", () => {
        if (localStorage.getItem("sidebarState") === "active") {
            sidebar.classList.add("active"); // Keep sidebar open if it was active
            content.classList.add("active"); // Adjust content width accordingly
        }
    });
}

// Function to update and display the current date and time in DD/MM/YYYY format
function updateDateTime() {
    let now = new Date(); // Get the current date and time

    // Extract the day, month, and year from the date
    let day = now.getDate().toString().padStart(2, '0'); // Get day (1-31) and ensure two digits (e.g., 07)
    let month = (now.getMonth() + 1).toString().padStart(2, '0'); // Get month (0-11), add 1 to match human format (1-12)
    let year = now.getFullYear(); // Get full year (e.g., 2025)

    // Extract hours, minutes, and seconds for real-time display
    let hours = now.getHours().toString().padStart(2, '0'); // Get hours (0-23) in two-digit format
    let minutes = now.getMinutes().toString().padStart(2, '0'); // Get minutes (0-59) in two-digit format
    let seconds = now.getSeconds().toString().padStart(2, '0'); // Get seconds (0-59) in two-digit format

    // Construct the formatted date-time string in DD/MM/YYYY HH:MM:SS format
    let dateString = `${day}/${month}/${year}`;
    let timeString = `${hours}:${minutes}:${seconds}`;

    // Update the HTML element with date on top and time below using <br> for line break
    document.getElementById("dateTime").innerHTML = `${dateString}<br>${timeString}`;
}

// Call updateDateTime every 1000 milliseconds (1 second) to keep the time updated
setInterval(updateDateTime, 1000);

// Call the function immediately so the date and time display as soon as the page loads
updateDateTime();

// Login Form Validation
document.addEventListener('DOMContentLoaded', function() {
    console.log('Login JS loaded');

    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            // Perform any custom validation or actions here
            console.log('Form submitted');
        });
    }
});

// Register Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const phone = document.getElementById('phone');
    const location = document.getElementById('location');
    const gender = document.getElementById('gender');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            checkInputs();
        });
    }

    function checkInputs() {
        // trim to remove the whitespaces
        const usernameValue = username.value.trim();
        const emailValue = email.value.trim();
        const phoneValue = phone.value.trim();
        const locationValue = location.value.trim();
        const genderValue = gender.value.trim();
        const passwordValue = password.value.trim();
        const confirmPasswordValue = confirmPassword.value.trim();
        
        let isValid = true;

        if(usernameValue === '') {
            setErrorFor(username, 'Username cannot be blank');
            isValid = false;
        } else if(usernameValue.length < 5) {
            setErrorFor(username, 'Username must be at least 5 characters');
            isValid = false;
        } else {
            setSuccessFor(username);
        }
        
        if(emailValue === '') {
            setErrorFor(email, 'Email cannot be blank');
            isValid = false;
        } else if (!isEmail(emailValue)) {
            setErrorFor(email, 'Not a valid email');
            isValid = false;
        } else {
            setSuccessFor(email);
        }

        if(phoneValue === '') {
            setErrorFor(phone, 'Phone number cannot be blank');
            isValid = false;
        } else {
            setSuccessFor(phone);
        }

        if(locationValue === '') {
            setErrorFor(location, 'Location cannot be blank');
            isValid = false;
        } else {
            setSuccessFor(location);
        }

        if(genderValue === '') {
            setErrorFor(gender, 'Gender cannot be blank');
            isValid = false;
        } else {
            setSuccessFor(gender);
        }
        
        if(passwordValue === '') {
            setErrorFor(password, 'Password cannot be blank');
            isValid = false;
        } else if(passwordValue.length < 6) {
            setErrorFor(password, 'Password must be at least 6 characters');
            isValid = false;
        } else {
            setSuccessFor(password);
        }
        
        if(confirmPasswordValue === '') {
            setErrorFor(confirmPassword, 'Confirm Password cannot be blank');
            isValid = false;
        } else if(passwordValue !== confirmPasswordValue) {
            setErrorFor(confirmPassword, 'Passwords do not match');
            isValid = false;
        } else {
            setSuccessFor(confirmPassword);
        }

        if (isValid){
            form.submit();
        }
    }

    function setErrorFor(input, message) {
        const formControl = input.parentElement;
        const small = formControl.querySelector('small');
        formControl.className = 'register-form-control error';
        small.innerText = message;
    }

    function setSuccessFor(input) {
        const formControl = input.parentElement;
        formControl.className = 'register-form-control success';
    }

    function isEmail(email) {
        return /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@(([^<>()[\]\.,;:\s@"]+\.)+[^<>()[\]\.,;:\s@"]{2,})$/i.test(email);
    }
});

// START OF forgotpassword.html
// Function to open the user's default email client with a pre-filled email
function sendEmail() {//gets called when the button is clicked.

    let email = document.getElementById("userEmail").value; // Get the user's email from the input field

    // Check if the email field is empty
     if (email.trim() === "") {
        alert("Please enter a valid email address.");
        return; // Stop execution if no email is entered
    }

    let subject = "Request for Help"; // The subject of the email

    let body = "Hello,%0D%0A%0D%0AI would like more information regarding..."; // The body of the email

    // Formatting the "mailto" link
    let mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    // Redirecting the user to the email client
    window.location.href = mailtoLink;
}
// END OF forgotpassword.html

// START OF frontpage.html
/** NAVIGATION MENU **/
const hamburger = document.getElementById("hamburger");
const navbar = document.getElementById("navbar");

if (hamburger && navbar) {
    hamburger.addEventListener("click", () => navbar.classList.toggle("active"));
}

/** FOOTER VISIBILITY **/
const footer = document.getElementById("footer");

if (footer) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                footer.style.visibility = entry.isIntersecting ? "visible" : "hidden";
                // Optional opacity transition
                // footer.style.opacity = entry.isIntersecting ? "1" : "0";
            });
        },
        { threshold: 0.3 } // Footer appears when at least 30% is visible
    );
    observer.observe(footer);
}
// END OF frontpage.html

// START OF admin.html
// Select all sidebar list items
const listItems = document.querySelectorAll(".sidebar li");

// Function to handle click (permanent selection)
function setActiveItem() {
    listItems.forEach((item) => item.classList.remove("active")); // Remove "active" from all items
    this.classList.add("active"); // Add "active" class to the clicked item
    localStorage.setItem("activeSidebarItem", this.dataset.item); // Save active item index in localStorage
}

// Function to handle hover (temporary effect)
function handleHover() {
    this.classList.add("hovered"); // Add "hovered" effect when mouse enters
}

// Function to remove hover effect when mouse leaves
function removeHover() {
    this.classList.remove("hovered"); // Remove "hovered" effect when mouse leaves
}

// Add event listeners to all list items
listItems.forEach((item, index) => {
    item.dataset.item = index; // Assign a unique index to each item for localStorage
    item.addEventListener("click", setActiveItem); // Listen for clicks (permanent selection)
    item.addEventListener("mouseenter", handleHover); // Listen for hover in (temporary effect)
    item.addEventListener("mouseleave", removeHover); // Listen for hover out (remove effect)
});

// Restore the active item from localStorage on page load
document.addEventListener("DOMContentLoaded", () => {
    const savedItem = localStorage.getItem("activeSidebarItem"); // Get saved active item index
    if (savedItem !== null) { // Check if there's a saved item
        listItems[savedItem].classList.add("active"); // Restore the saved active item
    }
});

// Sidebar Menu Toggle Logic
const toggle = document.querySelector(".toggle"); // Select the sidebar toggle button
const sidebar = document.querySelector(".sidebar"); // Select the sidebar
const content = document.querySelector(".content"); // Select the content area

if (toggle && sidebar && content) {
    // Toggle sidebar open/close on click
    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("active"); // Toggle sidebar "active" state
        content.classList.toggle("active"); // Adjust content width accordingly

        // Save sidebar state in localStorage
        localStorage.setItem("sidebarState", sidebar.classList.contains("active") ? "active" : "");
    });

    // Restore sidebar state from localStorage on page load
    document.addEventListener("DOMContentLoaded", () => {
        if (localStorage.getItem("sidebarState") === "active") {
            sidebar.classList.add("active"); // Keep sidebar open if it was active
            content.classList.add("active"); // Adjust content width accordingly
        }
    });
}

// Function to update and display the current date and time in DD/MM/YYYY format
function updateDateTime() {
    let now = new Date(); // Get the current date and time

    // Extract the day, month, and year from the date
    let day = now.getDate().toString().padStart(2, '0'); // Get day (1-31) and ensure two digits (e.g., 07)
    let month = (now.getMonth() + 1).toString().padStart(2, '0'); // Get month (0-11), add 1 to match human format (1-12)
    let year = now.getFullYear(); // Get full year (e.g., 2025)

    // Extract hours, minutes, and seconds for real-time display
    let hours = now.getHours().toString().padStart(2, '0'); // Get hours (0-23) in two-digit format
    let minutes = now.getMinutes().toString().padStart(2, '0'); // Get minutes (0-59) in two-digit format
    let seconds = now.getSeconds().toString().padStart(2, '0'); // Get seconds (0-59) in two-digit format

    // Construct the formatted date-time string in DD/MM/YYYY HH:MM:SS format
    let dateString = `${day}/${month}/${year}`;
    let timeString = `${hours}:${minutes}:${seconds}`;

    // Update the HTML element with date on top and time below using <br> for line break
    document.getElementById("dateTime").innerHTML = `${dateString}<br>${timeString}`;
}

// Call updateDateTime every 1000 milliseconds (1 second) to keep the time updated
setInterval(updateDateTime, 1000);

// Call the function immediately so the date and time display as soon as the page loads
updateDateTime();
// END OF admin.html