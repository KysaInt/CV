(() => {
    const params = new URLSearchParams(window.location.search);
    const focus = params.get('focus');
    if (!focus) return;

    const decodedFocus = decodeURIComponent(focus);
    let focused = false;

    function matches(element) {
        const values = [
            element.getAttribute('src'),
            element.getAttribute('data-fullsrc'),
            element.getAttribute('alt'),
            element.textContent,
        ].filter(Boolean).join(' ');
        return values.includes(decodedFocus);
    }

    function focusTarget() {
        if (focused) return;
        const elements = [...document.querySelectorAll('img, iframe, video, .gallery-item, .featured-card')];
        const target = elements.find(matches) || elements.find((element) => {
            const nested = element.querySelector?.('img, iframe, video');
            return nested && matches(nested);
        });
        if (!target) return;
        focused = true;
        target.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
        target.classList.add('focus-work-target');
        window.setTimeout(() => target.classList.remove('focus-work-target'), 2200);
    }

    const style = document.createElement('style');
    style.textContent = '.focus-work-target { outline: 4px solid rgba(255, 152, 0, 0.9); outline-offset: 8px; transition: outline 0.3s ease; }';
    document.head.appendChild(style);
    focusTarget();
    new MutationObserver(focusTarget).observe(document.body, { childList: true, subtree: true });
    window.setTimeout(focusTarget, 800);
    window.setTimeout(focusTarget, 1800);
})();
