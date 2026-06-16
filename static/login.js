//Auto-focus on the username field
document.addEventListener('DOMContentLoaded', function(){ //DOMContentLoaded will be fired when the page fully loads
    document.getElementById('username').focus(); //Automatically places cursor inside username field
});

//Disables the button on submit
document.getElementById('login-form').addEventListener('submit', function(){
    const btn = document.getElementById('loginBtn');
    btn.textContent = 'Signing in...'; //Changes the button text from Login to Signing in
    btn.disabled = true; //Disables the button so the user can't click on it again
});

//Fades out the error message when the user starts typing in the input fields
document.querySelectorAll('input').forEach(function(input){ //Selects all input fields and watches them for any typing activity
    input.addEventListener('input', function(){ //The event 'input' is fired every time a user types, deletes or changes anything inside that input field
        const error = document.querySelector('.error-message'); //Stores the element with the class 'error-message' inside the variable error
        if (error){ //Checks if the variable error actually exists on the login page
            error.style.opacity = '0'; //Makes the error invisible, hides it
            error.style.transition = 'opacity 0.3s ease'; //Error fades out over 0.3 seconds instead of disappearing suddenly
        }
    }); //End of the event listener 
}); //End of the forEach loop that loops through every input element on the page