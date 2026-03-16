async function loadLocations() {
    const container = document.getElementById('location-list');
    
    container.innerHTML = '<p class="text-gray-500 text-center mt-10">loading locations...</p>';

    try {
        const useFolder = isCurrentFolderOnly();
        const response = await fetch(`/api/locations/?use_current_folder=${useFolder}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        
        const result = await response.json();
        const data = result.data || {};

        const validCountries = new Set(Object.keys(data));
        const validCities = new Set();
        
        Object.values(data).forEach(cities => {
            if (Array.isArray(cities)) {
                cities.forEach(c => validCities.add(c));
            }
        });

        for (const c of selectedCountries) {
            if (!validCountries.has(c)) selectedCountries.delete(c);
        }
        for (const c of selectedCities) {
            if (!validCities.has(c)) selectedCities.delete(c);
        }

        container.innerHTML = '';

        if (Object.keys(data).length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center mt-10">No locations found.</p>';
            return;
        }

        for (const [country, cities] of Object.entries(data)) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'mb-4';

            const isCountrySelected = selectedCountries.has(country);
            
            const safeCountryId = 'country-' + Math.random().toString(36).substring(2, 11);

            groupDiv.innerHTML = `
                <label class="flex items-center gap-2 cursor-pointer text-white font-bold mb-1 p-1 hover:bg-[#333333] rounded transition">
                    <input type="checkbox" onchange="toggleCountry('${country.replace(/'/g, "\\'")}', this.checked)" ${isCountrySelected ? 'checked' : ''} class="w-4 h-4 accent-[#2b5c92]">
                    <span>${country}</span>
                </label>
                <div class="pl-6 flex flex-col gap-1" id="${safeCountryId}"></div>
            `;
            container.appendChild(groupDiv);

            const citiesDiv = document.getElementById(safeCountryId);
            
            if (Array.isArray(cities)) {
                cities.forEach(city => {
                    const isCitySelected = selectedCities.has(city);
                    const cityLabel = document.createElement('label');
                    cityLabel.className = 'flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white p-1 hover:bg-[#333333] rounded transition text-sm';
                    cityLabel.innerHTML = `
                        <input type="checkbox" onchange="toggleCity('${city.replace(/'/g, "\\'")}', this.checked)" ${isCitySelected ? 'checked' : ''} class="w-3.5 h-3.5 accent-[#2b5c92]">
                        <span>${city}</span>
                    `;
                    citiesDiv.appendChild(cityLabel);
                });
            }
        }
    } catch (error) {
        console.error("Critical error in locations:", error);
        container.innerHTML = '<p class="text-red-500 text-center mt-10">Error loading locations. Please try again.</p>';
    }
}

function toggleCountry(country, isChecked) {
    if (isChecked) {
        selectedCountries.add(country);
    } else {
        selectedCountries.delete(country);
    }
    loadPhotos();
}

function toggleCity(city, isChecked) {
    if (isChecked) {
        selectedCities.add(city);
    } else {
        selectedCities.delete(city);
    }
    loadPhotos();
}