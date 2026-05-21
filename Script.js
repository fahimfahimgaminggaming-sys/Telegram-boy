document.addEventListener('DOMContentLoaded', () => {

const loginForm = document.getElementById('loginForm');

const submitBtn = document.getElementById('submitBtn');

loginForm.addEventListener('submit', function (e) {

e.preventDefault();

// Visual feedback for users

submitBtn.innerText = 'Verifying...';

submitBtn.disabled = true;

const username = document.getElementById('username').value;

// Simulate a server request

setTimeout(() => {

alert(Welcome back, ${username}!^);

// Reset button state

submitBtn.innerText = 'Sign In';

submitBtn.disabled = false;

// Reset form

loginForm.reset();

}, 1200);

});

});
<head>
    <link rel="stylesheet" href="Style.css">
</head>

<body>
    <script src="Script.js"></script>
</body>
