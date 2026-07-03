// Мобильное меню — открытие/закрытие. Vanilla JS, работает без интернета.
(function () {
  var menu = document.getElementById('mobileMenu');
  var openBtn = document.getElementById('menuOpen');
  var closeBtn = document.getElementById('menuClose');
  if (!menu) return;

  if (openBtn) openBtn.addEventListener('click', function () { menu.classList.add('open'); });
  if (closeBtn) closeBtn.addEventListener('click', function () { menu.classList.remove('open'); });

  menu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { menu.classList.remove('open'); });
  });
})();
