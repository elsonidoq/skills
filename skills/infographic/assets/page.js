/* Glossed terms. Inlined only when a page actually has a glossary, so a page
 * without one stays pure markup. Click toggles; Escape and a click elsewhere
 * close. The tooltip is centred on its term and then clamped into the viewport,
 * because a term near the right edge of a phone screen would otherwise open a
 * tooltip half of which is off the page. */
(function () {
  var PAD = 8;

  function close(btn) {
    btn.setAttribute('aria-expanded', 'false');
    btn.querySelector('.gloss-text').style.transform = '';
  }

  function closeAll(except) {
    var open = document.querySelectorAll('.gloss[aria-expanded="true"]');
    for (var i = 0; i < open.length; i++) if (open[i] !== except) close(open[i]);
  }

  function open(btn) {
    btn.setAttribute('aria-expanded', 'true');
    var tip = btn.querySelector('.gloss-text');
    tip.style.transform = '';
    var box = tip.getBoundingClientRect();
    var shift = 0;
    if (box.right > window.innerWidth - PAD) shift = window.innerWidth - PAD - box.right;
    if (box.left + shift < PAD) shift = PAD - box.left;
    if (shift) tip.style.transform = 'translateX(calc(-50% + ' + Math.round(shift) + 'px))';
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.gloss') : null;
    closeAll(btn);
    if (!btn) return;
    if (btn.getAttribute('aria-expanded') === 'true') close(btn);
    else open(btn);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll(null);
  });
})();
