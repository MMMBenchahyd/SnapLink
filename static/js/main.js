/*=============== Showing nav bar menu ===============*/
const navMenu = document.getElementById('nav-menu'),
  navToggle = document.getElementById('nav-toggle'),
  navClose = document.getElementById('nav-close');

/* Menu show */
if (navToggle) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.add('show-menu');
  });
}

/* Menu hidden */
if (navClose) {
  navClose.addEventListener('click', () => {
    navMenu.classList.remove('show-menu');
  });
}

/*=============== Remove Menuu for mobile ===============*/
const navLink = document.querySelectorAll('.nav__link');

const linkAction = () => {
  const navMenu = document.getElementById('nav-menu');
  // When we click on each nav__link, we remove the show-menu class
  //  Tested=100% working
  navMenu.classList.remove('show-menu');
};
navLink.forEach((n) => n.addEventListener('click', linkAction));

/*=============== adding some blure for header  ===============*/
const blurHeader = () => {
  const header = document.getElementById('header');
  // adding a class if the bottom offset is greater than 50 of the viewport
  this.scrollY >= 50
    ? header.classList.add('blur-header')
    : header.classList.remove('blur-header');
};
window.addEventListener('scroll', blurHeader);

/*================== image tools/upload  scripts ================== */

/*====  this script show the name of the selected file ======*/
document.getElementById('file').addEventListener('change', function () {
  const label = document.querySelector('.custom-file-label');
  const fileName = this.files[0]?.name || 'Choose Your Image';
  label.textContent = fileName;
});
//======================================================
// dynamic upload gallery with link and thums

const fileInput = document.getElementById('file');
const label = document.querySelector('.custom-file-label');
const cancelButton = document.getElementById('cancel-button');
const contentInput = document.getElementById('content');
const form = document.querySelector('form');

// function to reset the file input and hide the
// cancel button if image is not selected yet
function resetFileInput() {
  fileInput.value = '';
  label.textContent = 'Choose Your Image';
  cancelButton.style.display = 'none';
}

// ensure the cancel button is hidden when the page loade
//  when uploading a new image or refreshing the page
window.addEventListener('load', resetFileInput);

// showing the cancel button when a file is selected
fileInput.addEventListener('change', function () {
  const fileName = this.files[0]?.name || 'Choose Your Image';
  label.textContent = fileName;

  // truncate file name if it's too long
  // applied for image name exceeding 20 character
  label.textContent =
    fileName.length > 20 ? `${fileName.substring(0, 17)}...` : fileName;

  // show cancel button if a file is selected
  cancelButton.style.display = this.files.length ? 'inline-block' : 'none';
});

// handling the cancel button to clear the file input
cancelButton.addEventListener('click', resetFileInput);

// On form (file name ) submission, we set content input to file name if it's empty
form.addEventListener('submit', (event) => {
  if (!contentInput.value.trim()) {
    const fileName = fileInput.files[0]?.name;
    if (fileName) {
      contentInput.value = fileName;
      // keep original file name
    }
  }
});

/**============= code for copy link ==================*/
// function to copying the link to clipboard

function openPopup(imageSrc, imgId, imageName, creationDate) {
  const popup = document.getElementById('image-popup');
  const popupImage = document.getElementById('popup-image');
  const detailContainer = document.querySelector('.thumbnail-description');
  const tableBody = document.querySelector('.popup-table tbody');

  // Update the popup image
  popupImage.src = imageSrc;

  // Update the details near the image
  detailContainer.innerHTML = `
            <p><span>Image Name:</span> ${imageName || 'Unknown'}</p>
            <p><span>Creation Date:</span> ${creationDate || 'Unknown'}</p>
            <p>
                            <span>
                                <a style="color: rgb(125, 0, 81);" href="#" onclick="openUpdatePopup('${imgId}')">Update image</a>
                            </span>
                        </p>
                        
                        <!-- Popup for updating the image filename -->
                        <div id="updateImagePopup" style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); z-index: 1000;">
                            <h3>Update Image Filename</h3>
                            <input type="text" id="newFilenameInput" placeholder="Enter new filename" />
                            <button onclick="submitUpdate()">Submit</button>
                            <button onclick="closeUpdatePopup()">Cancel</button>
                        </div>
                        
                        <!-- Overlay to darken the background -->
                        <div id="overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 999;"></div>
            <p><span><a style="color: rgb(125, 0, 81);" href="#" onclick="downloadImage('${imgId}')">Download 
                        image</a></span></p>
            <p><span><a style="color: rgb(125, 0, 81);" href="#" onclick="deleteImage('${imgId}')">Delete image</a></span></p>
        `;
  tableBody.innerHTML = `
            <tr>
                <td>Direct Link</td>
                <td>snap-link.site/image/${imgId}</td>
                <td>
                    <button onclick="copyLink('snap-link.site/image/${imgId}', this)">copy</button>
                </td>
            </tr>
            <tr>
                <td>GitHub Markdown</td>
                <td>![Image](snap-link.site/image/${imgId})</td>
                <td>
                    <button onclick="copyLink('![Image](snap-link.site/image/${imgId})', this)">copy</button>
                </td>
            </tr>
            <tr>
                <td>Thumbnail for Website</td>
                <td>&lt;img src="snap-link.site/image/${imgId}" alt="Thumbnail"&gt;</td>
                <td>
                    <button onclick="copyLink('&lt;img src=&quot;snap-link.site/image/${imgId}&quot; alt=&quot;Thumbnail&quot;&gt;', this)">copy</button>
                </td>
            </tr>
        `;

  // Show the popup
  popup.style.display = 'flex';
}

//Popup box close button
function closePopup() {
  const popup = document.getElementById('image-popup');
  popup.style.display = 'none';
}

function copyLink(link, button) {
  const tempInput = document.createElement('input');
  tempInput.value = link;
  document.body.appendChild(tempInput);
  tempInput.select();
  document.execCommand('copy');
  document.body.removeChild(tempInput);

  // Change the button text (copy) to "Copied"
  button.innerText = 'copied';
  setTimeout(() => {
    button.innerText = 'copy';
  }, 1500); // 1.5s delays
}
//////// addedd~~~~~~~~~~~~~~by simo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
async function deleteImage(imgId) {
  // Confirm deletion with the user
  const confirmDelete = confirm('Are you sure you want to delete this image?');
  if (!confirmDelete) return;

  try {
    // Send DELETE request to the API
    const response = await fetch(`/api/delete/${imgId}`, {
      method: 'DELETE',
    });

    // Check if the request was successful
    if (response.ok) {
      const data = await response.json();
      alert('Image deleted successfully!');
      console.log('Success:', data);
      // Optionally, remove the image from the DOM
      //document.querySelector(`[data-img-id="${imgId}"]`).remove();
      location.reload();
    } else {
      // Handle errors
      const errorData = await response.json();
      alert(
        'Failed to delete image: ' + (errorData.message || 'Unknown error')
      );
      console.error('Error:', errorData);
    }
  } catch (error) {
    // Handle network errors
    alert('Network error. Please try again.');
    console.error('Network Error:', error);
  }
}

async function downloadImage(imgId) {
  try {
    // Send GET request to retrieve the image
    const response = await fetch(`/api/retrieve/${imgId}`);

    // Check if the request was successful
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to download image');
    }

    // Parse the response JSON
    const data = await response.json();

    // Convert base64 image data to a Blob
    const byteCharacters = atob(data.image_data); // Decode base64
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: data.content_type });

    // Create a temporary link element to trigger the download
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = data.filename; // Set the filename for the download
    document.body.appendChild(link);
    link.click(); // Trigger the download
    document.body.removeChild(link); // Clean up

    console.log('Image downloaded successfully:', data.filename);
  } catch (error) {
    alert(error.message || 'Failed to download image');
    console.error('Download Error:', error);
  }
}
