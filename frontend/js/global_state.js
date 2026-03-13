let selectedPersonIds = new Set();
let selectedCountries = new Set();
let selectedCities = new Set();

function isCurrentFolderOnly() {
    const chk = document.getElementById('chk-current-folder');
    return chk ? chk.checked : false;
}