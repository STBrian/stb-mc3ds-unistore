async function loadFeatureMods() {
    const jsonFeaturedIndexPath = "assets/mods-indexes/featured_mods.json";

    try {
        const response = await fetch(jsonFeaturedIndexPath);
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const data = await response.json();
        const featuredMods = data.featured_mods;
        const featuredModsContainer = document.getElementById("featured-mods");

        for (const mod of featuredMods) {
            const jsonModFilePath = "assets/mods-info/" + mod + ".json";

            try {
                const response2 = await fetch(jsonModFilePath);
                if (!response2.ok) {
                    throw new Error('Network response was not ok ' + response2.statusText);
                }
                const data2 = await response2.json();

                const entryContainer = document.createElement("div");
                entryContainer.className = "contenedor";
                const imgContainer = document.createElement("div");
                const modInfoContainer = document.createElement("div");

                const imgModBanner = document.createElement("img");
                imgModBanner.src = data2.modBanner;
                imgModBanner.className = "imagen-centrada";
                imgContainer.appendChild(imgModBanner);

                const modTitle = document.createElement("h1");
                modTitle.textContent = data2.modTitle;
                modInfoContainer.appendChild(modTitle);
                const modDescription = document.createElement("p");
                modDescription.textContent = data2.modShortDescription;
                modDescription.style = "text-align: center;";
                modInfoContainer.appendChild(modDescription);
                const modSeeMoreButton = document.createElement("button");
                modSeeMoreButton.className = "button";
                modSeeMoreButton.textContent = "See more";
                modSeeMoreButton.addEventListener('click', function() {goToPage('modPage.html', 'mod', mod);});
                modInfoContainer.appendChild(modSeeMoreButton);

                entryContainer.appendChild(imgContainer);
                entryContainer.append(modInfoContainer);

                featuredModsContainer.appendChild(entryContainer);
            } catch (error) {
                console.error('Could not load featured mod:', mod, error);
            }
        }
    } catch (error) {
        console.error('Could not load featured mods: ', error);
    }
}

document.addEventListener('DOMContentLoaded', loadFeatureMods);