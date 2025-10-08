function getDevices() {
    fetch('/devices')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched devices data:", data);
            const select = document.getElementById('camera');
            select.innerHTML = '';

            if (Array.isArray(data)) {
                data.forEach(device => {
                    select.innerHTML += `<option value="${device.id}">${device.name}</option>`;
                });
                document.getElementById('status').innerText = "Devices loaded successfully.";
            } else {
                document.getElementById('status').innerText = "No devices found or unexpected response.";
                console.error("Expected an array but got:", data);
            }
        })
        .catch(error => {
            console.error("Error fetching devices:", error);
            document.getElementById('status').innerText = "Error fetching devices.";
        });
}


function startPreview() {
    const source = document.getElementById('camera').value;
    let blur = parseInt(document.getElementById('blur').value);
    const background = document.getElementById('background').value;
    const fps = parseInt(document.getElementById('fps').value);

    // Ensure blur is odd
    if (blur % 2 === 0) blur += 1;

    const preview = document.getElementById('preview');
    preview.src = `/preview?source=${source}&fps=${fps}&blur_strength=${blur}&background=${background}`;
    setStatus(`Previewing camera ${source} with blur ${blur}, background: ${background}`);
}

function stopPreview() {
    const preview = document.getElementById('preview');
    preview.src = '';  // This stops the MJPEG stream on frontend

    fetch('/stop_preview') 
        .then(response => response.json())
        .then(data => {
            setStatus(data.message);
        })
        .catch(error => {
            console.error("Error stopping preview:", error);
            setStatus("Error stopping preview.");
        });
}

function startStream() {
    stopPreview(); 
    const source = document.getElementById('camera').value;
    const fps = document.getElementById('fps').value;
    const blur = document.getElementById('blur').value;
    const background = document.getElementById('background').value;

    fetch(`/start?source=${source}&fps=${fps}&blur=${blur}&background=${background}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').innerText = data.message;  
        });
}

function stopStream() {
    fetch('/stop')
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').innerText = data.message;
        });
}

function updateBlurValue(value) {
    document.getElementById('blurValue').innerText = `Blur Strength: ${value}`;
}
