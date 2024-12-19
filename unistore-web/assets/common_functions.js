function goToPage(url, name, param) {
    window.location.href = `${url}?${name}=${encodeURIComponent(param)}`
}

function getParam(url, param) {
    const params = new URLSearchParams(url.split('?')[1]);
    return params.get(param);
}

function formatText(text) {
    const breakLinesPattern = /\n/g
    var parsedText = text.replace(breakLinesPattern, '<br>');

    const urlPattern = /(\b(https?|ftp):\/\/[^\s/$.?#].[^\s]*)/gi;
    parsedText = parsedText.replace(urlPattern, (url) => {
        return `<a href="${url}" target="_blank" class="break-link">${url}</a>`;
    });

    return parsedText;
}