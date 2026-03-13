function updateTimeFilter() {
    selectedDateFrom = document.getElementById('input-date-from').value;
    selectedDateTo = document.getElementById('input-date-to').value;
    
    loadPhotos();
}

function clearTimeFilter() {
    selectedDateFrom = '';
    selectedDateTo = '';
    
    document.getElementById('input-date-from').value = '';
    document.getElementById('input-date-to').value = '';
    
    loadPhotos();
}

function setTimePreset(preset) {
    const currentYear = new Date().getFullYear();
    let start = '';
    let end = '';

    if (preset === 'this_year') {
        start = `${currentYear}-01-01`;
        end = `${currentYear}-12-31`;
    } else if (preset === 'last_year') {
        start = `${currentYear - 1}-01-01`;
        end = `${currentYear - 1}-12-31`;
    }

    selectedDateFrom = start;
    selectedDateTo = end;

    document.getElementById('input-date-from').value = start;
    document.getElementById('input-date-to').value = end;

    loadPhotos();
}