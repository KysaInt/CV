(function(){
  const prevTops = new WeakMap();

  function handleSlideAnimation() {
    const elements = document.querySelectorAll('.slide-animate');
    const windowHeight = window.innerHeight;
    elements.forEach(el => {
      const rect = el.getBoundingClientRect();
      const prevTop = prevTops.get(el);
      const isVisible = rect.top < windowHeight && rect.bottom > 0;

      if (isVisible) {
        const enteringFromTop = prevTop !== undefined && (prevTop <= 0 || (prevTop + rect.height) <= 0);
        // 默认认为从下进入或已在视口内
        const enteringFromBottom = prevTop !== undefined && prevTop >= windowHeight;

        el.classList.remove('down', 'visible-up', 'visible-down');
        if (enteringFromTop) {
          // 从上方进入: 先 -60px, 再到 0
          el.classList.add('visible-down');
        } else {
          // 从下进入或已在视口内: 先 +60px, 再到 0
          el.classList.add('visible-up');
        }
      } else {
        // 不可见时, 根据在视口的上下位置预设偏移
        el.classList.remove('visible-up', 'visible-down');
        if (rect.top >= windowHeight) {
          // 在视口下方: 保持 +60px 初始偏移
          el.classList.remove('down');
        } else if (rect.bottom <= 0) {
          // 在视口上方: 设置 -60px 预偏移
          el.classList.add('down');
        }
      }

      prevTops.set(el, rect.top);
    });
  }

  function init() {
    document.querySelectorAll('.slide-animate').forEach(el => {
      el.classList.remove('visible-up', 'visible-down', 'down');
      const rect = el.getBoundingClientRect();
      if (rect.top >= window.innerHeight) {
        el.classList.remove('down');
      } else if (rect.bottom <= 0) {
        el.classList.add('down');
      }
      prevTops.set(el, rect.top);
    });
    handleSlideAnimation();
    setTimeout(handleSlideAnimation, 100);
  }

  window.addEventListener('scroll', handleSlideAnimation, { passive: true });
  window.addEventListener('resize', handleSlideAnimation);

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();