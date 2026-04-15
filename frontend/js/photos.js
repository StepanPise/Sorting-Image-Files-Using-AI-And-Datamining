async function loadPhotos() {
    try {
        const params = new URLSearchParams();

        if (selectedPersonIds.size > 0) {
            params.append('people', Array.from(selectedPersonIds).join(','));
        }

        selectedCountries.forEach(country => params.append('country', country));
        selectedCities.forEach(city => params.append('city', city));

        if (isCurrentFolderOnly()) {
            params.append('use_current_folder', 'true');
        }

        if (selectedDateFrom) params.append('date_from', selectedDateFrom);
        if (selectedDateTo) params.append('date_to', selectedDateTo);

// --- NOVÉ FILTRY PRO OTHERS ---
        if (typeof selectedOrientations !== 'undefined' && selectedOrientations.size > 0) {
            selectedOrientations.forEach(ori => params.append('orientation', ori));
        }

        const minW = document.getElementById('input-min-width')?.value;
        if (minW) params.append('min_width', minW);

        const maxW = document.getElementById('input-max-width')?.value;
        if (maxW) params.append('max_width', maxW);

        const minH = document.getElementById('input-min-height')?.value;
        if (minH) params.append('min_height', minH);

        const maxH = document.getElementById('input-max-height')?.value;
        if (maxH) params.append('max_height', maxH);


        const url = `/api/photos?${params.toString()}`;
        console.log("Fetching URL:", url);
        
        const response = await fetch(url);
        const result = await response.json();

        const grid = document.getElementById('photo-grid');
        grid.innerHTML = ''; 

        if (!result.data || result.data.length === 0) {
            grid.innerHTML = '<p class="text-gray-500 col-span-full text-center mt-10">No photos found.</p>';
            return;
        }

        result.data.forEach((photo, index) => {
            const photoDiv = document.createElement('div');
            photoDiv.className = 'aspect-square bg-[#333333] rounded overflow-hidden border border-gray-700 hover:border-[#2b5c92] transition cursor-pointer shadow-lg relative group';

            photoDiv.onclick = () => openLightbox(index, result.data);

            photoDiv.innerHTML = `
                <img src="/api/photos/${photo.id}/file" loading="lazy" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition">

            `;
            
            grid.appendChild(photoDiv);
        });
    } catch (error) {
        console.error("Error loading photos:", error);
    }
}



async function exportPhotos() {
    const btn = document.getElementById('btn-export');
    const originalText = btn.innerText;
    btn.innerText = "Exporting...";
    btn.disabled = true;
    btn.classList.add("opacity-50", "cursor-wait");

    try {
        const params = new URLSearchParams();

        if (selectedPersonIds.size > 0) {
            params.append('people', Array.from(selectedPersonIds).join(','));
        }
        selectedCountries.forEach(country => params.append('country', country));
        selectedCities.forEach(city => params.append('city', city));
        if (isCurrentFolderOnly()) {
            params.append('use_current_folder', 'true');
        }
        if (selectedDateFrom) params.append('date_from', selectedDateFrom);
        if (selectedDateTo) params.append('date_to', selectedDateTo);


        // --- NOVÉ FILTRY PRO OTHERS ---
        if (typeof selectedOrientations !== 'undefined' && selectedOrientations.size > 0) {
            selectedOrientations.forEach(ori => params.append('orientation', ori));
        }

        const minW = document.getElementById('input-min-width')?.value;
        if (minW) params.append('min_width', minW);

        const maxW = document.getElementById('input-max-width')?.value;
        if (maxW) params.append('max_width', maxW);

        const minH = document.getElementById('input-min-height')?.value;
        if (minH) params.append('min_height', minH);

        const maxH = document.getElementById('input-max-height')?.value;
        if (maxH) params.append('max_height', maxH);


        const response = await fetch(`/api/photos/export?${params.toString()}`, {
            method: 'POST'
        });
        
        const result = await response.json();

        if (result.status === "cancelled") {
                    return;
        }

        if (result.status === "ok") {
            // alert(`Export successful!\nCopied ${result.exported} photos.\nErrors: ${result.errors}`);
        } else {
            alert(`Export failed: ${result.message}`);
        }

    } catch (error) {
        console.error("Export error:", error);
        alert("An error occurred during export");
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
        btn.classList.remove("opacity-50", "cursor-wait");
    }
}