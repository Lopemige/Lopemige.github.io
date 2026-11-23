/* Site scripts: language switch (English or Spanish) and the contact form. No libraries. */
(function () {
  'use strict';

  var ES = window.I18N_ES || {};
  var lang = 'en';
  var originals = new WeakMap();   /* the English text of every element, so we can switch back */

  /* ---------- Saved choice, link choice, browser language ---------- */

  function saved() {
    try { return window.localStorage.getItem('lang'); } catch (e) { return null; }
  }
  function save(value) {
    try { window.localStorage.setItem('lang', value); } catch (e) { /* private mode: fine */ }
  }
  function fromLink() {
    var m = /[?&]lang=(en|es)(?:&|$)/.exec(window.location.search);
    return m ? m[1] : null;
  }
  function browserIsSpanish() {
    var first = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    return /^es(?:-|$)/i.test(first);
  }

  /* ---------- Switching the page ---------- */

  function say(key, fallback) {
    return lang === 'es' && ES[key] ? ES[key] : fallback;
  }

  function apply(next) {
    lang = next;
    document.documentElement.setAttribute('lang', next);

    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var o = originals.get(el) || {};
      if (o.text === undefined) { o.text = el.textContent; originals.set(el, o); }
      el.textContent = next === 'es' && ES[el.getAttribute('data-i18n')] ? ES[el.getAttribute('data-i18n')] : o.text;
    });

    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var o = originals.get(el) || {};
      if (o.html === undefined) { o.html = el.innerHTML; originals.set(el, o); }
      el.innerHTML = next === 'es' && ES[el.getAttribute('data-i18n-html')] ? ES[el.getAttribute('data-i18n-html')] : o.html;
    });

    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      var parts = el.getAttribute('data-i18n-attr').split(':');
      var name = parts[0], key = parts[1];
      var o = originals.get(el) || {};
      o.attrs = o.attrs || {};
      if (o.attrs[name] === undefined) { o.attrs[name] = el.getAttribute(name); originals.set(el, o); }
      el.setAttribute(name, next === 'es' && ES[key] ? ES[key] : o.attrs[name]);
    });

    var button = document.getElementById('lang-toggle');
    if (button) {
      button.textContent = next === 'es' ? 'English' : 'Español';
      button.setAttribute('lang', next === 'es' ? 'en' : 'es');
    }
  }

  function initLanguage() {
    var wanted = fromLink() || saved() || (browserIsSpanish() ? 'es' : 'en');
    if (fromLink()) save(fromLink());
    if (wanted === 'es') apply('es');

    var button = document.getElementById('lang-toggle');
    if (button) {
      button.addEventListener('click', function () {
        var next = lang === 'es' ? 'en' : 'es';
        save(next);
        apply(next);
      });
    }
  }

  /* ---------- Footer year ---------- */

  function initYear() {
    var y = String(new Date().getFullYear());
    document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = y; });
  }

  /* ---------- Contact form (Web3Forms) ---------- */

  function initContact() {
    var form = document.getElementById('contact-form');
    if (!form) return;
    var status = document.getElementById('form-status');
    var button = form.querySelector('button[type="submit"]');

    function show(text, state) {
      status.textContent = text;
      status.setAttribute('data-state', state || '');
    }

    form.addEventListener('submit', function (event) {
      var key = form.elements.access_key.value;
      if (!key || key.indexOf('YOUR_ACCESS_KEY') === 0) {
        event.preventDefault();
        show(say('js.off', 'This form is not switched on yet.'), 'error');
        return;
      }
      if (!window.fetch) return;   /* old browser: let the form post normally */

      event.preventDefault();
      button.disabled = true;
      show(say('js.sending', 'Sending...'), '');

      var body = {};
      new FormData(form).forEach(function (value, name) { body[name] = value; });

      fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(body)
      })
        .then(function (response) { return response.json(); })
        .then(function (result) {
          if (!result || !result.success) throw new Error('rejected');
          form.reset();
          show(say('js.sent', 'Thanks, your message was sent. I will reply by email.'), 'success');
        })
        .catch(function () {
          show(say('js.fail', 'Your message was not sent. Check your connection and try again.'), 'error');
        })
        .then(function () { button.disabled = false; });
    });
  }

  initYear();
  initLanguage();
  initContact();
})();
