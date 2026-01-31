document.addEventListener('DOMContentLoaded', () => {
  const sticky = document.getElementById('sticky-title');
  if (!sticky) return;
  const stickyText = sticky.querySelector('.sticky-title-text') || sticky;
  const hiddenStyles = {
    opacity: '0',
    transform: 'translateY(-100%)',
    pointerEvents: 'none'
  };
  const visibleStyles = {
    opacity: '1',
    transform: 'translateY(0)',
    pointerEvents: 'auto'
  };

  sticky.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
  const headings = Array.from(document.querySelectorAll('h1, h3'));
  if (headings.length === 0) return;

  function pickActiveHeading() {
    // 选择当前视口顶部附近的最后一个标题
    let active = headings[0];
    for (const h of headings) {
      const rect = h.getBoundingClientRect();
      if (rect.top <= 80) {
        active = h;
      } else {
        break;
      }
    }
    return active;
  }

  function updateSticky() {
    const active = pickActiveHeading();
    const text = (active.dataset.title || active.textContent || '').trim();
    if (text) stickyText.textContent = text;

    const shouldShow = window.scrollY > 20;
    if (shouldShow) {
      Object.assign(sticky.style, visibleStyles);
      document.body.style.paddingTop = `${sticky.offsetHeight}px`;
    } else {
      Object.assign(sticky.style, hiddenStyles);
      document.body.style.paddingTop = '0px';
    }
  }

  const observer = new IntersectionObserver(() => updateSticky(), {
    root: null,
    rootMargin: '0px 0px -80% 0px',
    threshold: [0, 1]
  });
  headings.forEach(h => observer.observe(h));

  window.addEventListener('scroll', updateSticky, { passive: true });
  window.addEventListener('resize', updateSticky);
  updateSticky();
});
