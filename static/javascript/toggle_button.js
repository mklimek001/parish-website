document.addEventListener('DOMContentLoaded', function() {
    var passwordButton = document.querySelector('.view-password-btn');
    
    if (passwordButton) {
        passwordButton.addEventListener('click', togglePassword);
    }
});

function togglePassword() {
    var passwordField = document.querySelector('input[name="password"]');
    var passwordButton = document.querySelector('.view-password-btn');
    
    if (passwordField.type === "password") {
        passwordField.type = "text";
        passwordButton.textContent = "🔒"; 
    } else {
        passwordField.type = "password";
        passwordButton.textContent = "👁️";
    }
}