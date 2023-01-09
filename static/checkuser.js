//
// This file handles the user input for the registration form
//

// Reset all values upon final load
window.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#Username").value = "";
    document.querySelector("#password").value = "";
    document.querySelector("#repeat").value = "";
    document.querySelector("#email").value = "";
});

// Check if username is valid
const user = document.querySelector("#Username");

user.addEventListener("input", async (e) => {
    let input = e.target.value;
    // Check if the entered username is longer than four characters
    if (input.length < 4 && input.length > 0) {
        document.querySelector("#checkuser").classList.remove("alert", "alert-danger", "alert-warning", "alert-success");
        document.querySelector("#checkuser").innerHTML = "Username must be longer than 4 characters";
        document.querySelector("#checkuser").classList.add("alert", "alert-warning");
    } else {
        // if no username is entered or the username > 0, reset the warnings
        document.querySelector("#checkuser").innerHTML = "";
        document.querySelector("#checkuser").classList.remove("alert", "alert-danger", "alert-warning", "alert-success");

        // Using the APi to check if the username exists
        const checkuser = await fetch("/checkuser/" + input);
        let answer = await checkuser.json();

        // if the APi returns something => show warning
        if (answer["count"] > 0) {
            document.querySelector("#checkuser").classList.add("alert", "alert-danger");
            document.querySelector("#checkuser").innerHTML = "Username is taken"
        } else {

            document.querySelector("#checkuser").classList.add("alert", "alert-success");
            document.querySelector("#checkuser").innerHTML = "Username available"
        }

    }
});


// Check if passwords match
const password1 = document.querySelector("#password");
const password2 = document.querySelector("#repeat");

// Add EventListener to first input field
password1.addEventListener("input", (e) => {
    let pwd1 = e.target.value;
    let pwd2 = document.querySelector("#repeat").value;
    if (!compare(pwd1, pwd2)) {
        document.querySelector("#pwdcheck").innerHTML = "Passwords don't match";
        document.querySelector("#pwdcheck").classList.add("alert", "alert-warning");
    } else {
        document.querySelector("#pwdcheck").innerHTML = "";
        document.querySelector("#pwdcheck").classList.remove("alert", "alert-warning");
    }
});

// Add EventListener to second input field
password2.addEventListener("input", (e) => {
    let pwd1 = e.target.value;
    let pwd2 = document.querySelector("#password").value;
    if (!compare(pwd1, pwd2)) {
        document.querySelector("#pwdcheck").innerHTML = "Passwords don't match";
        document.querySelector("#pwdcheck").classList.add("alert", "alert-warning");
    } else {
        document.querySelector("#pwdcheck").innerHTML = "";
        document.querySelector("#pwdcheck").classList.remove("alert", "alert-warning");
    }
});

// This helper unction compares the two passwords
const compare = (pass1, pass2) => {
    if (pass1 !== pass2) {
        return false;
    } else {
        return true;
    }
}