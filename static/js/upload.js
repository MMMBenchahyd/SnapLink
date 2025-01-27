function openUploadPopup() {
  console.log('Opening upload popup...');
  document.getElementById('uploadPopup').style.display = 'block';
  document.getElementById('uploadOverlay').style.display = 'block';
}

function closeUploadPopup() {
  console.log('Closing upload popup...');
  document.getElementById('uploadPopup').style.display = 'none';
  document.getElementById('uploadOverlay').style.display = 'none';
  document.getElementById('uploadForm').reset();
  document.getElementById('uploadStatus').textContent = '';
}

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });
    const result = await response.json();

    if (response.ok) {
      document.getElementById('uploadStatus').textContent =
        'Upload successful!';
      document.getElementById('uploadStatus').style.color = 'green';
      setTimeout(location.reload(), 2000);
    } else {
      throw new Error(result.error || 'Upload failed');
    }
  } catch (error) {
    document.getElementById('uploadStatus').textContent = error.message;
    document.getElementById('uploadStatus').style.color = 'red';
  }
});
