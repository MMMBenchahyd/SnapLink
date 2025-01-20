/*=============== Showing nav bar menu ===============*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/* Menu show */
if(navToggle){
    navToggle.addEventListener('click', () =>{
        navMenu.classList.add('show-menu')
    })
}

/* Menu hidden */
if(navClose){
    navClose.addEventListener('click', () =>{
        navMenu.classList.remove('show-menu')
    })
}

/*=============== Remove Menuu for mobile ===============*/
const navLink = document.querySelectorAll('.nav__link')

const linkAction = () =>{
    const navMenu = document.getElementById('nav-menu')
    // When we click on each nav__link, we remove the show-menu class
    //  Tested=100% working 
    navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))


/*=============== adding some blure for header  ===============*/
const blurHeader = () =>{
    const header = document.getElementById('header')
    // adding a class if the bottom offset is greater than 50 of the viewport
    this.scrollY >= 50 ? header.classList.add('blur-header') 
                       : header.classList.remove('blur-header')
}
window.addEventListener('scroll', blurHeader)


/*================== image tools/upload  scripts ================== */

/*====  this script show the name of the selected file ======*/
document.getElementById('file').addEventListener('change', function() {
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
        label.textContent = fileName.length > 20 ? `${fileName.substring(0, 17)}...` : fileName;

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
            <p><span><a style="color: rgb(125, 0, 81);" href="/update/${imgId}">Rename image</a></span></p>
            <p><span><a style="color: rgb(125, 0, 81);" href="/retrieve/${imgId}">Download image</a></span></p>
            <p><span><a style="color: rgb(125, 0, 81);" href="/delete/${imgId}">Delete image</a></span></p>
        `;
        tableBody.innerHTML = `
            <tr>
                <td>Direct Link</td>
                <td>/image/${imgId}</td>
                <td>
                    <button onclick="copyLink('/image/${imgId}', this)">copy</button>
                </td>
            </tr>
            <tr>
                <td>GitHub Markdown</td>
                <td>![Image](/image/${imgId})</td>
                <td>
                    <button onclick="copyLink('![Image](/image/${imgId})', this)">copy</button>
                </td>
            </tr>
            <tr>
                <td>Thumbnail for Website</td>
                <td>&lt;img src="/image/${imgId}" alt="Thumbnail"&gt;</td>
                <td>
                    <button onclick="copyLink('&lt;img src=&quot;/image/${imgId}&quot; alt=&quot;Thumbnail&quot;&gt;', this)">copy</button>
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
    