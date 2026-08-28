(() => {
    const overlay = document.getElementById('fullscreen-overlay');
    const fullscreenImage = document.getElementById('fullscreen-image');
    if (!overlay || !fullscreenImage) return;

    const selector = document.body.dataset.lightboxSelector || '.gallery img';
    const clearOnClose = document.body.dataset.lightboxClear === 'true';
    let escHandler = null;

    function closeOverlay() {
        overlay.style.display = 'none';
        if (clearOnClose) fullscreenImage.src = '';
        if (escHandler) {
            document.removeEventListener('keydown', escHandler);
            escHandler = null;
        }
    }

    document.addEventListener('click', event => {
        const image = event.target.closest(selector);
        if (!image) return;
        fullscreenImage.src = image.dataset.fullsrc || image.src;
        fullscreenImage.alt = image.alt || '全屏展示';
        overlay.style.display = 'flex';
        if (!escHandler) {
            escHandler = event => {
                if (event.key === 'Escape') closeOverlay();
            };
            document.addEventListener('keydown', escHandler);
        }
    });

    overlay.addEventListener('click', closeOverlay);
})();