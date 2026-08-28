document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.expandable').forEach(element => {
        element.addEventListener('click', () => {
            const details = document.getElementById(element.dataset.target);
            if (!details) return;
            details.style.display = details.style.display === 'block' ? 'none' : 'block';
        });
    });

    const savedY = localStorage.getItem('resumeScrollY');
    if (savedY !== null) {
        window.scrollTo(0, Number.parseInt(savedY, 10));
        localStorage.removeItem('resumeScrollY');
    }

    document.querySelectorAll('a.portfolio-link').forEach(link => {
        link.addEventListener('click', () => {
            localStorage.setItem('resumeScrollY', String(window.scrollY));
        });
    });
});