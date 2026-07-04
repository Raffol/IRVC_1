/**
 * Мобильное меню — открытие/закрытие через кнопки-гамбургеры.
 * Загружается на всех страницах.
 */
(function () {
  var menu = document.getElementById('mobileMenu');
  var openBtn = document.getElementById('menuOpen');
  var closeBtn = document.getElementById('menuClose');
  if (!menu) return;

  if (openBtn) openBtn.addEventListener('click', function () {
    menu.classList.add('open');
    document.body.style.overflow = 'hidden';
  });

  function close() {
    menu.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (closeBtn) closeBtn.addEventListener('click', close);

  // Закрываем при клике на любую ссылку внутри меню
  menu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', close);
  });

  // Закрытие по Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.classList.contains('open')) close();
  });
})();
