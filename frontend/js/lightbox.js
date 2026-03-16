let currentPhotoArray = [];
let currentPhotoIndex = 0;

function openLightbox(index, photosData) {
    currentPhotoArray = photosData;
    currentPhotoIndex = index;
    
    document.getElementById('lightbox').classList.remove('hidden');
    document.getElementById('lightbox').classList.add('flex');
    
    updateLightboxContent();
}

function closeLightbox() {
    document.getElementById('lightbox').classList.add('hidden');
    document.getElementById('lightbox').classList.remove('flex');
    document.getElementById('lightbox-img').src = "";
}

function prevPhoto() {
    if (currentPhotoArray.length === 0) return;
    currentPhotoIndex = (currentPhotoIndex - 1 + currentPhotoArray.length) % currentPhotoArray.length;
    updateLightboxContent();
}

function nextPhoto() {
    if (currentPhotoArray.length === 0) return;
    currentPhotoIndex = (currentPhotoIndex + 1) % currentPhotoArray.length;
    updateLightboxContent();
}

function updateLightboxContent() {
    const photo = currentPhotoArray[currentPhotoIndex];
    const imgEl = document.getElementById('lightbox-img');
    const infoEl = document.getElementById('lightbox-info');

    imgEl.src = `/api/photos/${photo.id}/file`; 
    
    infoEl.innerText = `${photo.filename} | ID: ${photo.id}`;
}

// keyboard navigation
document.addEventListener('keydown', (e) => {
    const lightbox = document.getElementById('lightbox');
    if (!lightbox.classList.contains('hidden')) {
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') prevPhoto();
        if (e.key === 'ArrowRight') nextPhoto();
    }
});

//-------BACKEND LOGIC-----------------

async function deleteCurrentPhoto() {
}

async function openInExplorer() {
}