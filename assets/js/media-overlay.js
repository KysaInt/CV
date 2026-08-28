(() => {
    const overlay = document.getElementById('fullscreen-overlay');
    const content = overlay?.querySelector('.overlay-content');
    if (!overlay || !content) return;

    const selector = document.body.dataset.mediaOverlaySelector || '.gallery-item iframe';
    let escHandler = null;

    function closeOverlay() {
        overlay.style.display = 'none';
        content.replaceChildren();
        if (escHandler) {
            document.removeEventListener('keydown', escHandler);
            escHandler = null;
        }
    }

    function openOverlay(source) {
        let media;
        if (source.tagName === 'VIDEO') {
            media = document.createElement('video');
            media.src = source.currentSrc || source.src;
            media.controls = true;
            media.autoplay = true;
        } else {
            media = document.createElement('iframe');
            media.src = source.src;
            media.allowFullscreen = true;
            media.setAttribute('allow', 'autoplay');
        }

        content.replaceChildren(media);
        overlay.style.display = 'flex';
        if (!escHandler) {
            escHandler = event => {
                if (event.key === 'Escape') closeOverlay();
            };
            document.addEventListener('keydown', escHandler);
        }
    }

    document.querySelectorAll(selector).forEach(media => {
        media.addEventListener('click', () => openOverlay(media));
    });
    overlay.addEventListener('click', closeOverlay);
})();