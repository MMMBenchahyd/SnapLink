// Function to open a popup
function openPopupL(popupId) {
  document.getElementById(popupId).style.display = 'flex'; //display in the centre of the window when opned
  document.getElementById('overlay').style.display = 'flex'; //display in the centre of the window when opned
}

// Function to close a popup
function closePopupL(popupId) {
  document.getElementById(popupId).style.display = 'none';
  document.getElementById('overlay').style.display = 'none';
}

// Event listeners for opening popups

document
  .getElementById('openLoginPopup')
  .addEventListener('click', function () {
    openPopupL('loginPopup');
  });

// Get all elements with the class 'openSignupPopup'
const signupButtons = document.querySelectorAll('.openSignupPopup');

// Loop through each button and add the event listener
signupButtons.forEach((button) => {
  button.addEventListener('click', function () {
    openPopupL('signupPopup');
  });
});

// Handle login form submission
document
  .getElementById('loginForm')
  .addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('loginIdentifie').value;
    const password = document.getElementById('loginPassword').value;

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to home page if login is successful
        window.location.href = '/';
      } else {
        // Show alert with error message
        alert(data.message || 'Invalid username/email or password');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred during login');
    }
  });

// Handle signup form submission
document
  .getElementById('signupForm')
  .addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    // check password
    const passwordError = checkPasswordQuality(password);
    if (passwordError) {
      alert(passwordError);
      return;
    }

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
        }),
      });

      // Check if the response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Unexpected response: ${text}`);
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Signup failed');
      }

      alert(
        'Signup successful! Please check your email to verify your account.'
      );
      console.log('Signup data:', data);
      closePopupL('signupPopup');
    } catch (error) {
      alert(error.message || 'Signup failed. Please try again.');
      console.error('Signup Error:', error);
    }
  });
// function to checkapsswd
function checkPasswordQuality(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  let errorMessage = '';

  if (password.length < minLength) {
    errorMessage += 'Password must be at least 8 characters long,';
  }
  if (!hasUpperCase) {
    errorMessage += ' at least one UPPERCASE letter,';
  }
  if (!hasLowerCase) {
    errorMessage += ' at least one lowercase letter,';
  }
  if (!hasNumbers) {
    errorMessage += ' at least one number,';
  }
  if (!hasSpecialChars) {
    errorMessage += 'at least one special character.';
  }

  return errorMessage.trim();
}

//  check on real timw
document
  .getElementById('signupPassword')
  .addEventListener('input', function (event) {
    const password = event.target.value;
    const passwordError = checkPasswordQuality(password);

    const passwordFeedback = document.getElementById('lilio');
    if (passwordError) {
      passwordFeedback.textContent = passwordError;
      passwordFeedback.style.color = 'red';
    } else {
      passwordFeedback.textContent = 'Password meets all requirements.';
      passwordFeedback.style.color = 'green';
    }
  });
