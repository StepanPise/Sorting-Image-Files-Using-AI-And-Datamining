let selectedPersonIds = new Set();

async function loadPeople() {
    try {
        const response = await fetch('/api/people');
        const result = await response.json();
        
        const container = document.getElementById('people-list');
        container.innerHTML = '';

        result.data.forEach(person => {
            const personDiv = document.createElement('div');
            
            const isSelected = selectedPersonIds.has(person.id);
            if (isSelected) {
                personDiv.className = 'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition border border-[#2b5c92] bg-[#2b5c92]/20';
            } else {
                personDiv.className = 'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition border border-transparent bg-[#333333] hover:border-gray-500';
            }            

            personDiv.onclick = (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') return;
                togglePersonSelection(person.id, personDiv);
            };

            personDiv.innerHTML = `
                <div class="w-10 h-10 rounded-full bg-[#2b5c92] flex-shrink-0 overflow-hidden">
                    <img src="/api/people/${person.id}/thumbnail" class="w-full h-full object-cover" onerror="this.style.display='none'">
                </div>
                
                <input type="text" id="input-${person.id}" value="${person.name}" 
                       onblur="savePersonName(${person.id}, this)" 
                       onkeydown="if(event.key === 'Enter') { this.blur(); }"
                       class="bg-[#252526] text-sm text-white px-2 py-1.5 rounded border border-gray-600 w-full focus:outline-none focus:border-[#2b5c92] transition">
                
                <span id="status-${person.id}" class="text-green-500 text-sm opacity-0 transition-opacity duration-300 font-bold">✓</span>
            `;

            container.appendChild(personDiv);
        });
    } catch (error) {
        console.error("Error:", error);
    }
}

function togglePersonSelection(personId, element) {
    if (selectedPersonIds.has(personId)) {
        selectedPersonIds.delete(personId);
        element.className = 'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition border border-transparent bg-[#333333] hover:border-gray-500';
    } else {
        selectedPersonIds.add(personId);
        element.className = 'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition border border-[#2b5c92] bg-[#2b5c92]/20';
    }
    console.log("Selected IDs:", Array.from(selectedPersonIds));
}

async function savePersonName(personId, inputElement) {
    const newName = inputElement.value.trim();
    if (!newName) return;

    try {
        const response = await fetch(`/api/people/${personId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName }) 
        });
        
        if (response.ok) {
            console.log(`Saved: ${newName}`);
            
            const statusIcon = document.getElementById(`status-${personId}`);
            statusIcon.classList.remove('opacity-0');
            setTimeout(() => {
                statusIcon.classList.add('opacity-0');
            }, 1500);
        } else {
            console.error("Server returned an error during save.");
        }
    } catch (error) {
        console.error("Communication error:", error);
    }
}