let currentImgId = null;

// Function to open the popup
function openUpdatePopup(imgId) {
  currentImgId = imgId; // Store the image ID
  document.getElementById('updateImagePopup').style.display = 'block';
  document.getElementById('overlay').style.display = 'block';
}

// Function to close the popup
function closeUpdatePopup() {
  document.getElementById('updateImagePopup').style.display = 'none';
  document.getElementById('overlay').style.display = 'none';
  document.getElementById('newFilenameInput').value = '';
  currentImgId = null; // Reset the image ID
}

// Function to submit the update
async function submitUpdate() {
  const newFilename = document.getElementById('newFilenameInput').value.trim();

  if (!newFilename) {
    alert('Please enter a new filename.');
    return;
  }

  if (!currentImgId) {
    alert('No image selected.');
    return;
  }

  try {
    // Send the update request to the backend
    const response = await fetch(`/api/update/${currentImgId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ newname: newFilename }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to update image');
    }

    const result = await response.json();
    alert('Image updated successfully!');

    location.reload();

    closeUpdatePopup(); // Close the popup after successful update
  } catch (error) {
    alert('Failed to update image: ' + error.message);
  }
}
