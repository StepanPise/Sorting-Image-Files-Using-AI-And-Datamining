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

    imgEl.src = `/api/photos/${photo.id}/file?t=${Date.now()}`; 
    
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
    const photo = currentPhotoArray[currentPhotoIndex];
    
    if (!confirm(`Are you sure you want to remove this photo from the database?\n${photo.filename}\n\n(The physical file will NOT be deleted from your disk)`)) return;
    
    try {
        const response = await fetch(`/api/photos/${photo.id}`, { method: 'DELETE' });
        const result = await response.json();

        if (result.status === "ok") {
            currentPhotoArray.splice(currentPhotoIndex, 1);
            
            refreshApp();

            // Close lightbox if last photo was deleted
            if (currentPhotoArray.length === 0) {
                closeLightbox();
            } else {
                if (currentPhotoIndex >= currentPhotoArray.length) {
                    currentPhotoIndex = currentPhotoArray.length - 1;
                }
                updateLightboxContent();
            }
        } else {
            alert(`Failed to remove photo: ${result.message}`);
        }
    } catch (e) {
        console.error("Communication error:", e);
        alert("Server error occurred");
    }
}

async function openInExplorer() {
    const photo = currentPhotoArray[currentPhotoIndex];
    
    try {
        const response = await fetch(`/api/photos/${photo.id}/open_explorer`, { method: 'POST' });
        const result = await response.json();
        
        if (result.status !== "ok") {
            alert(`Failed to open Explorer: ${result.message}`);
        }
    } catch (e) {
        console.error("Communication error:", e);
        alert("Server error occurred");
    }
}