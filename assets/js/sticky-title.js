document.addEventListener('DOMContentLoaded', () => {
  const sticky = document.getElementById('sticky-title');
  if (!sticky) return;
  const stickyText = sticky.querySelector('.sticky-title-text') || sticky;
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
