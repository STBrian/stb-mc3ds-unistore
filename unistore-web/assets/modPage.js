function loadModContent() {
    const param = getParam(window.location.href, 'mod');
    if (param) {
        const jsonFilePath = "assets/mods-info/" + param + ".json";
        fetch(jsonFilePath)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                document.title = `${data.modTitle} - STB's MC3DS Mods`;

                document.getElementById('headerModTitle').textContent = data.modTitle;
                document.getElementById('modTitle').textContent = data.modTitle;
                document.getElementById('modDescription').innerHTML = formatText(data.modDescription);
                document.getElementById('modVersion').textContent = data.modVersion;
                document.getElementById('modIcon').src = data.modIcon;
                document.getElementById("modBanner").style.backgroundImage = `url(${data.modBanner})`;
                
                const downloadContainer = document.getElementById("download-container");
                const downloadButton = document.createElement("a");
                downloadButton.href = data.downloadLink;
                downloadButton.className = "button";
                downloadButton.textContent = "Download";
                downloadContainer.appendChild(downloadButton);

                const contenedor = document.getElementById("screenshots");
                const screenshots = data.screenshots;
                screenshots.forEach(url => {
                    const img = document.createElement("img");
                    img.src = url;
                    img.alt = 'Screenshot';
                    contenedor.appendChild(img);
                });
            })
            .catch(error => {
                console.error('There was an error with fetch: ', error);
                window.location.href = "notFound.html?" + encodeURIComponent(param);
            });
    } else {
        console.error("No param mod found!");
        window.location.href = "notFound.html";
    }
}

document.addEventListener('DOMContentLoaded', loadModContent);