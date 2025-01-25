fetch('assets/topnavbar/topnavbar.html')
    .then(response => response.text())
    .then(html => {
        document.getElementById('topnavbar').innerHTML = html;
    })
    .catch(error => console.error("Unable to load topnavbar:", error));