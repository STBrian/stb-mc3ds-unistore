function goToPage(url, name, param) {
    window.location.href = `${url}?${name}=${encodeURIComponent(param)}`
}

function getParam(url, param) {
    const params = new URLSearchParams(url.split('?')[1]);
    return params.get(param);
}

function replaceLinesBreaks(text) {
    return text.replace(/\n/g, '<br>');
}