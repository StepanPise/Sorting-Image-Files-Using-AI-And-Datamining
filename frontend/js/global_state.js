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