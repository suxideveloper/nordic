// ═══════════════════════════════════════════
//  NORDIC UNIVERSITY PORTAL — Main JS
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // AOS Init
  AOS.init({ duration: 700, once: true, offset: 60 });

  // Navbar scroll effect
  const navbar = document.getElementById('mainNavbar');
  window.addEventListener('scroll', () => {
    navbar?.classList.toggle('scrolled', window.scrollY > 50);
  });

  // Counter animation for stats
  document.querySelectorAll('.stat-number[data-target]').forEach(el => {
    const target = +el.dataset.target;
    let count = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      count = Math.min(count + step, target);
      el.textContent = count + (el.dataset.suffix || '');
      if (count >= target) clearInterval(timer);
    }, 25);
  });

  // Auto-dismiss alerts
  setTimeout(() => {
    document.querySelectorAll('.nordic-alert').forEach(a => {
      bootstrap.Alert.getOrCreateInstance(a)?.close();
    });
  }, 4000);

  // Search form: trim empty params
  document.querySelectorAll('form.filter-form').forEach(form => {
    form.addEventListener('submit', () => {
      form.querySelectorAll('input, select').forEach(el => {
        if (!el.value.trim()) el.disabled = true;
      });
    });
  });
});
