// script.js
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.login').addEventListener('submit', function(event) {
        event.preventDefault();
        // Call the Python function or handle the form submission here
    });
});

const myPopup = new Popup({
    id: "my-popup",
    title: "Username Already exist !",
    content: `
        Please use a different username.`,
});

const myPopup2 = new Popup({
    id: "my-popup",
    title: "Invalid Data !",
    content: "Invalid username or password",
});


async function hashData(data) {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // convert buffer to byte array
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); // convert bytes to hex string
    return hashHex;
}

async function createAccount() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        return;
    }

    try {
        const hash_user = await hashData(username);
        const hash_pwd = await hashData(password);

        // console.log('Username:', hash_user, 'Password:', hash_pwd);

        fetch('/create_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: hash_user, password: hash_pwd })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Info:", data); 
            if (data.message.includes('UNIQUE')) {
                myPopup.show();
            }
        })
        .catch(error => {
            console.error('Error:', error); // Log any other errors that occur during the request
        });

    } catch (error) {
        console.error("Hashing error:", error);
    }
}


async function loginAccount() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        return;
    }

    try {
        const hash_user = await hashData(username);
        const hash_pwd = await hashData(password);

        fetch('/login_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: hash_user, password: hash_pwd })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Redirect to dashboard.html
                window.location.href = '/dashboard'; // Update the path if necessary
            } else if (data.message.includes('Invalid')) {
                myPopup2.show();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

    } catch (error) {
        console.error("Hashing error:", error);
    }
}
