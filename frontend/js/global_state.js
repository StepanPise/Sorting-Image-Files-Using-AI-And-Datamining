let selectedPersonIds = new Set();
let selectedCountries = new Set();
let selectedCities = new Set();

let selectedDateFrom = '';
let selectedDateTo = '';


function isCurrentFolderOnly() {
    const chk = document.getElementById('chk-current-folder');
    return chk ? chk.checked : false;
}


async function refreshApp() {
    await Promise.all([
        loadPeople(),
        loadLocations()
    ]);
    
    await loadPhotos();
}

async function resetAllFilters(){
    selectedPersonIds = new Set();
    selectedCountries = new Set();
    selectedCities = new Set();

    clearTimeFilter()

    await refreshApp();
}

async function toggleCurrentFolderFilter() {
    await refreshApp();
}

async function savePreference(key, value) {
    try {
        await fetch(`/api/preferences/${key}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ value: String(value) }) 
        });
        console.log(`Preference saved: ${key} = ${value}`);
    } catch (e) {
        console.error("Failed to save preference:", e);
    }
}

async function loadPreferences() {
    try {
        const response = await fetch('/api/preferences');
        const result = await response.json();

        if (result.status === "ok" && result.data) {
            const prefs = result.data;

            if (prefs['face_detection_enabled'] !== undefined) {
                document.getElementById('chk-detect').checked = (prefs['face_detection_enabled'] === "true");
            }

            if (prefs['use_current_folder_only'] !== undefined) {
                document.getElementById('chk-current-folder').checked = (prefs['use_current_folder_only'] === "true");
            }

            if (prefs['min_photos_per_person'] !== undefined) {
                document.getElementById('min-photos').value = prefs['min_photos_per_person'];
            }
        }
    } catch (e) {
        console.error("Failed to load preferences:", e);
    }
}

async function wipeDatabase() {
    const isConfirmed = confirm('This will delete ALL photos, faces, and people from the database.\n\nDo you want to continue?');
    
    if (!isConfirmed) {
        return; 
    }

    try {
        const response = await fetch('/api/system/wipe', {
            method: 'POST'
        });
        
        const result = await response.json();

        if (result.status === "ok") {
            window.location.reload(); 
        } else {
            alert("Error wiping database: " + result.message);
        }

    } catch (error) {
        console.error("Communication error during database wipe:", error);
        alert("Failed to communicate with the server");
    }
}