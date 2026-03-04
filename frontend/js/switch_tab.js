function switchTab(tab){
    const tabs = ['others','people','time','location']

    //reset all tabs
    tabs.forEach(tab => {
        document.getElementById(`tab-${tab}`).classList.add('hidden');
        document.getElementById(`tab-${tab}`).classList.remove('flex');
        document.getElementById(`btn-tab-${tab}`).className = "flex-1 py-3 text-gray-400 hover:text-white hover:bg-[#2d2d2d] transition";

    });
 
    // turn on the selected one
    document.getElementById(`tab-${tab}`).classList.remove('hidden');
    document.getElementById(`tab-${tab}`).classList.add('flex');
    document.getElementById(`btn-tab-${tab}`).className = "flex-1 py-3 bg-[#2b5c92] text-white transition";


    if (tab === 'location') {
        loadLocations();
    }
}