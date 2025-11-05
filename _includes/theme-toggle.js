<script>
(() => {
  const html = document.documentElement;
  const toggle = document.getElementById('theme-toggle');

  // 1. Read saved preference
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  const setTheme = (theme) => {
    html.dataset.theme = theme;
    toggle.checked = (theme === 'light');
    localStorage.setItem('theme', theme);
  };

  // Initial theme
  if (saved === 'light' || saved === 'dark') {
    setTheme(saved);
  } else {
    setTheme(prefersDark ? 'dark' : 'light');
  }

  // 2. Click handler
  toggle.addEventListener('change', () => {
    setTheme(toggle.checked ? 'light' : 'dark');
  });

  // 3. Respect OS changes while manual override exists
  window.matchMedia('(prefers-color-scheme: dark)')
        .addEventListener('change', e => {
          if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
          }
        });
})();
</script>
