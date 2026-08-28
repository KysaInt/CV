(() => {
    let escHandler = null;

    function closeModal() {
        document.querySelector('.img-zoom-modal')?.remove();
        if (escHandler) {
            document.removeEventListener('keydown', escHandler);
            escHandler = null;
        }
    }

    document.addEventListener('click', event => {
        const image = event.target.closest('.zoomable-img');
        if (!image || document.querySelector('.img-zoom-modal')) return;

        const modal = document.createElement('div');
        modal.className = 'img-zoom-modal';
        const zoomImage = document.createElement('img');
        zoomImage.src = image.dataset.fullsrc || image.src;
        zoomImage.alt = image.alt;
        modal.appendChild(zoomImage);
        document.body.appendChild(modal);
        modal.addEventListener('click', closeModal);
        escHandler = event => {
            if (event.key === 'Escape') closeModal();
        };
        document.addEventListener('keydown', escHandler);
    });
})();