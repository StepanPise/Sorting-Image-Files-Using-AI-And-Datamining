async function loadPhotos(personIds = []) {
    try {
        let url = '/api/photos';
        if (personIds.length > 0) {
            url += `?people=${personIds.join(',')}`;
        }

        const response = await fetch(url);
        const result = await response.json();

        const grid = document.getElementById('photo-grid');
        grid.innerHTML = ''; 

        result.data.forEach(photo => {
            const photoDiv = document.createElement('div');
            photoDiv.className = 'aspect-square bg-[#333333] rounded overflow-hidden border border-gray-700 hover:border-[#2b5c92] transition cursor-pointer shadow-lg relative group';

            photoDiv.innerHTML = `
                <img src="/api/photos/${photo.id}/file" loading="lazy" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition">
            `;
            
            grid.appendChild(photoDiv);
        });
    } catch (error) {
        console.error("Error loading photos:", error);
    }
}