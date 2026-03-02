let progressInterval; 

async function checkProgress() {
    try {
        const res = await fetch('/api/scanner/progress');
        const data = await res.json();
        
        if (data.is_scanning || data.progress > 0) {
            document.getElementById('progress-container').classList.remove('hidden');
            
            const percent = Math.round(data.progress * 100);
            document.getElementById('progress-bar').style.width = percent + '%';
            document.getElementById('progress-percent').innerText = percent + '%';
            document.getElementById('progress-text').innerText = data.message;
        }
    } catch (e) {
        console.error("progress check error", e);
    }
}

async function startScanning() {
    const detectFaces = document.getElementById('chk-detect').checked;
    const btn = document.getElementById('btn-scan');
    const originalText = btn.innerText;
    
    btn.innerText = "Scanning...";
    btn.disabled = true;
    btn.classList.add("opacity-50", "cursor-not-allowed");

    document.getElementById('progress-bar').style.width = '0%';
    progressInterval = setInterval(checkProgress, 500);

    try {
        const response = await fetch('/api/scanner/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ detect_faces: detectFaces })
        });
        
        const data = await response.json();
        if (data.status === "ok") {

            loadPeople(); 
        }
    } catch (error) {
        console.error("Scanning error:", error);
    } finally {
        clearInterval(progressInterval);
        
        setTimeout(() => {
            document.getElementById('progress-container').classList.add('hidden');
        }, 1500);

        btn.innerText = originalText;
        btn.disabled = false;
        btn.classList.remove("opacity-50", "cursor-not-allowed");
    }
}