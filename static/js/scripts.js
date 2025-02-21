const form = document.getElementById('registerForm');
const username = document.getElementById('username');
const email = document.getElementById('email');
const password = document.getElementById('password');
const confirmPassword = document.getElementById('confirmPassword');

form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    checkInputs();
});

function checkInputs() {
    // trim to remove the whitespaces
    const usernameValue = username.value.trim();
    const emailValue = email.value.trim();
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