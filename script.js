function validateRegisterForm() {

    const username =
        document.getElementById("username").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    const confirmPassword =
        document.getElementById("confirm_password").value;


    if (username.length < 3) {

        alert("Username must contain at least 3 characters.");

        return false;
    }


    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    if (!emailPattern.test(email)) {

        alert("Please enter a valid email address.");

        return false;
    }


    if (password.length < 8) {

        alert("Password must contain at least 8 characters.");

        return false;
    }


    if (!/[A-Za-z]/.test(password)) {

        alert("Password must contain at least one letter.");

        return false;
    }


    if (!/[0-9]/.test(password)) {

        alert("Password must contain at least one number.");

        return false;
    }


    if (password !== confirmPassword) {

        alert("Passwords do not match.");

        return false;
    }


    return true;
}