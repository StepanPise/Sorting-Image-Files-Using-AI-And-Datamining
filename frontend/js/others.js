let selectedOrientations = new Set();

function toggleOrientation(type) {
    const btn = document.getElementById(`btn-ori-${type}`);
    
    if (selectedOrientations.has(type)) {
        selectedOrientations.delete(type);
        btn.classList.remove('bg-[#2b5c92]', 'text-white', 'border-[#3a75b8]');
        btn.classList.add('bg-[#252526]', 'text-gray-300', 'border-gray-600');
    } else {
        selectedOrientations.add(type);
        btn.classList.remove('bg-[#252526]', 'text-gray-300', 'border-gray-600');
        btn.classList.add('bg-[#2b5c92]', 'text-white', 'border-[#3a75b8]');
    }
    
    refreshApp();
}

function clearOthersFilter() {
    selectedOrientations.clear();
    
    ['landscape', 'portrait', 'square'].forEach(type => {
        const btn = document.getElementById(`btn-ori-${type}`);
        if(btn) {
            btn.classList.remove('bg-[#2b5c92]', 'text-white', 'border-[#3a75b8]');
            btn.classList.add('bg-[#252526]', 'text-gray-300', 'border-gray-600');
        }
    });

    document.getElementById('input-min-width').value = '';
    document.getElementById('input-max-width').value = '';
    document.getElementById('input-min-height').value = '';
    document.getElementById('input-max-height').value = '';

    refreshApp();
}