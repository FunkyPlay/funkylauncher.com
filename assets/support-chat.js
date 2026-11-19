/* Funky Launcher — окно чата поддержки на сайте.
   Сервер: https://api.funkylauncher.com/support/ (служба чата Боты, тот же, что у лаунчера).
   Номер и секрет хранятся только в localStorage этого браузера (не cookie). */
(function () {
  'use strict';
  var API = 'https://api.funkylauncher.com/support';
  var STORE = 'fl_support_v1';
  var EN = (document.documentElement.lang || '').slice(0, 2) === 'en';
  var T = EN ? {
    btn: 'Support', title: 'Funky Launcher support', hello: 'Ask about the launcher or a modlist — we reply here, usually within a day. Keep this page or come back later: replies are saved in this browser.',
    ph: 'Your message…', send: 'Send', attach: 'Screenshot', close: 'Close',
    consent: 'We will receive your message, a screenshot (if you attach one) and a random ID saved in this browser — only to reply to you. Data is stored on our server in Germany: screenshots for 90 days, messages and replies for 12 months after your last contact. Don\'t send passwords or personal documents. You can delete your data at any time with the button below or by writing "delete my data" — we will do it within 10 working days.',
    ok: 'Got it', more: 'Privacy policy', policy: '/legal.html#support-chat-site-en',
    shotWarn: 'A screenshot may show private windows or other people\'s chats — check it before sending.',
    you: 'You', sup: 'Support', id: 'Your ID', del: 'Delete my data',
    delAsk: 'Delete all your messages and replies on our server? This cannot be undone.', deleted: 'Your data has been deleted.',
    file: 'File', fileBad: 'Only PNG or JPG up to 10 MB.', sending: 'Sending…',
    e429: 'Too many messages. Please try again in an hour.', eNet: 'No connection to the support server. Try again a bit later.', eGen: 'Could not send. Try again a bit later.'
  } : {
    btn: 'Поддержка', title: 'Поддержка Funky Launcher', hello: 'Спросите про лаунчер или сборку — ответим здесь, обычно в течение дня. Можно закрыть страницу и вернуться позже: переписка сохраняется в этом браузере.',
    ph: 'Ваше сообщение…', send: 'Отправить', attach: 'Скриншот', close: 'Закрыть',
    consent: 'Мы получим ваш текст, скриншот (если приложите) и случайный номер, сохранённый в этом браузере, — только чтобы ответить вам. Данные хранятся на нашем сервере в Германии: скриншоты 90 дней, сообщения и ответы 12 месяцев после последнего обращения. Не отправляйте пароли и личные документы. Удалить данные можно в любой момент кнопкой ниже или написав «удалить мои данные» — сделаем за 10 рабочих дней.',
    ok: 'Понятно', more: 'Политика конфиденциальности', policy: '/legal.html#support-chat-site',
    shotWarn: 'На скриншоте могут быть личные окна и чужие переписки — проверьте перед отправкой.',
    you: 'Вы', sup: 'Поддержка', id: 'Ваш номер', del: 'Удалить мои данные',
    delAsk: 'Удалить все ваши сообщения и ответы на нашем сервере? Отменить будет нельзя.', deleted: 'Ваши данные удалены.',
    file: 'Файл', fileBad: 'Только PNG или JPG до 10 МБ.', sending: 'Отправляю…',
    e429: 'Слишком много сообщений. Попробуйте через час.', eNet: 'Нет связи с сервером поддержки. Попробуйте чуть позже.', eGen: 'Не получилось отправить. Попробуйте чуть позже.'
  };

  function load() { try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) { return {}; } }
  function save() { try { localStorage.setItem(STORE, JSON.stringify(st)); } catch (e) { /* приватный режим */ } }
  function rnd(n) {
    var a = new Uint8Array(n); (window.crypto || window.msCrypto).getRandomValues(a);
    var s = ''; for (var i = 0; i < a.length; i++) s += String.fromCharCode(a[i]);
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  var st = load();               // {install, key, consent, seen}
  var msgs = [], last = 0, timer = null, file = null, open = false;

  var css = '.flsc-b{position:fixed;right:16px;bottom:16px;z-index:9998;display:flex;align-items:center;gap:.5rem;padding:.8rem 1.1rem;border:0;border-radius:999px;background:#ff3fd2;color:#14000f;font:700 1rem "Segoe UI",system-ui,sans-serif;cursor:pointer;box-shadow:0 10px 30px -8px rgba(255,63,210,.7)}' +
    '.flsc-b svg{width:20px;height:20px}.flsc-b i{position:absolute;top:4px;right:6px;width:10px;height:10px;border-radius:50%;background:#7ae8ff;display:none}.flsc-b.new i{display:block}' +
    '.flsc-b:focus-visible,.flsc button:focus-visible,.flsc a:focus-visible,.flsc textarea:focus-visible{outline:3px solid #7ae8ff;outline-offset:2px}' +
    '.flsc{position:fixed;right:16px;bottom:16px;z-index:9999;width:min(380px,calc(100vw - 32px));height:min(600px,calc(100vh - 32px));display:none;flex-direction:column;background:#11111c;border:1px solid #24243a;border-radius:16px;color:#fff;font:.95rem/1.45 "Segoe UI",system-ui,sans-serif;box-shadow:0 20px 60px -10px rgba(0,0,0,.8);overflow:hidden}' +
    '.flsc.on{display:flex}.flsc h2{flex:1;margin:0;font-size:1rem}.flsc-h{display:flex;align-items:center;gap:.5rem;padding:.8rem 1rem;border-bottom:1px solid #24243a;background:linear-gradient(95deg,rgba(255,63,210,.18),rgba(122,232,255,.12))}' +
    '.flsc-x{background:none;border:0;color:#b3b3c6;font-size:1.4rem;line-height:1;cursor:pointer;padding:.2rem .4rem}' +
    '.flsc-l{flex:1;overflow-y:auto;padding:.8rem 1rem;display:flex;flex-direction:column;gap:.6rem}' +
    '.flsc-m{max-width:85%;padding:.5rem .7rem;border-radius:12px;background:#1b1b2b;white-space:pre-wrap;overflow-wrap:anywhere}.flsc-m.me{align-self:flex-end;background:#3a1233}' +
    '.flsc-m small{display:block;color:#b3b3c6;font-size:.75rem;margin-bottom:.15rem}.flsc-m a{color:#7ae8ff}.flsc-n{color:#b3b3c6;font-size:.85rem}' +
    '.flsc-c{padding:.7rem 1rem;border-top:1px solid #24243a;font-size:.8rem;color:#b3b3c6}.flsc-c button{margin-top:.4rem}' +
    '.flsc-f{display:flex;flex-direction:column;gap:.4rem;padding:.7rem 1rem;border-top:1px solid #24243a}' +
    '.flsc textarea{width:100%;min-height:64px;max-height:160px;resize:vertical;box-sizing:border-box;padding:.5rem .6rem;border:1px solid #24243a;border-radius:10px;background:#07070d;color:#fff;font:inherit}' +
    '.flsc-r{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}.flsc-r span{flex:1;font-size:.8rem;color:#b3b3c6;overflow-wrap:anywhere}' +
    '.flsc-s,.flsc-a,.flsc-c button{border:0;border-radius:10px;padding:.5rem .9rem;font:700 .9rem "Segoe UI",system-ui,sans-serif;cursor:pointer}.flsc-s,.flsc-c button{background:#ff3fd2;color:#14000f}.flsc-a{background:#24243a;color:#fff}' +
    '.flsc-s:disabled{opacity:.5;cursor:default}.flsc-e{color:#ff8a9a;font-size:.8rem;min-height:1em}' +
    '.flsc-z{padding:.5rem 1rem .7rem;font-size:.75rem;color:#b3b3c6;display:flex;gap:.6rem;flex-wrap:wrap;align-items:center}.flsc-z a,.flsc-z button{color:#7ae8ff;background:none;border:0;padding:0;font:inherit;text-decoration:underline;cursor:pointer}' +
    '@media (max-width:480px){.flsc{right:0;bottom:0;width:100vw;height:100vh;height:100dvh;border-radius:0}.flsc-b{right:12px;bottom:12px}}';

  var s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }

  var btn = el('button', 'flsc-b'); btn.type = 'button'; btn.setAttribute('aria-haspopup', 'dialog');
  btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/></svg><i></i>';
  btn.appendChild(document.createTextNode(T.btn));

  var box = el('div', 'flsc'); box.setAttribute('role', 'dialog'); box.setAttribute('aria-label', T.title);
  var head = el('div', 'flsc-h'); head.appendChild(el('h2', '', T.title));
  var x = el('button', 'flsc-x', '×'); x.type = 'button'; x.setAttribute('aria-label', T.close); head.appendChild(x);
  var list = el('div', 'flsc-l'); list.setAttribute('aria-live', 'polite');
  var consent = el('div', 'flsc-c');
  consent.appendChild(el('div', '', T.consent));
  var okb = el('button', '', T.ok); okb.type = 'button'; consent.appendChild(okb);
  var form = el('form', 'flsc-f');
  var ta = el('textarea'); ta.placeholder = T.ph; ta.maxLength = 4000; ta.setAttribute('aria-label', T.ph);
  var row = el('div', 'flsc-r');
  var ab = el('button', 'flsc-a', T.attach); ab.type = 'button';
  var fi = el('input'); fi.type = 'file'; fi.accept = 'image/png,image/jpeg'; fi.hidden = true;
  var fname = el('span');
  var sb = el('button', 'flsc-s', T.send); sb.type = 'submit';
  row.appendChild(ab); row.appendChild(fname); row.appendChild(sb);
  var er = el('div', 'flsc-e');
  form.appendChild(ta); form.appendChild(row); form.appendChild(fi); form.appendChild(er);
  var foot = el('div', 'flsc-z');
  var pol = el('a', '', T.more); pol.href = T.policy; pol.target = '_blank'; pol.rel = 'noopener';
  var idl = el('span'); var delb = el('button', '', T.del); delb.type = 'button';
  foot.appendChild(idl); foot.appendChild(delb); foot.appendChild(pol);
  box.appendChild(head); box.appendChild(list); box.appendChild(consent); box.appendChild(form); box.appendChild(foot);

  function idShow() {
    idl.textContent = st.install ? T.id + ': ' + st.install.slice(0, 8) : '';
    delb.style.display = st.install ? '' : 'none';
    consent.style.display = st.consent ? 'none' : '';
  }

  function render() {
    list.textContent = '';
    list.appendChild(el('div', 'flsc-n', T.hello));
    msgs.forEach(function (m) {
      var me = m.from === 'player';
      var b = el('div', 'flsc-m' + (me ? ' me' : ''));
      b.appendChild(el('small', '', (me ? T.you : T.sup) + ' · ' + (m.time || '')));
      if (m.text) b.appendChild(document.createTextNode(m.text));
      if (m.file) {
        var a = el('a', '', '📎 ' + m.file); a.href = '#';
        a.addEventListener('click', function (ev) { ev.preventDefault(); getFile(m.id, m.file); });
        if (m.text) b.appendChild(document.createElement('br'));
        b.appendChild(a);
      }
      list.appendChild(b);
    });
    list.scrollTop = list.scrollHeight;
  }

  function q() { return 'install=' + encodeURIComponent(st.install) + '&key=' + encodeURIComponent(st.key); }

  function poll(markSeen) {
    if (!st.install) return Promise.resolve();
    return fetch(API + '/messages?' + q() + '&after=' + last, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (arr) {
        if (!Array.isArray(arr) || !arr.length) return;
        arr.forEach(function (m) { msgs.push(m); if (m.id > last) last = m.id; });
        var lastSup = 0; msgs.forEach(function (m) { if (m.from === 'support' && m.id > lastSup) lastSup = m.id; });
        if (open || markSeen) { st.seen = lastSup; save(); }
        btn.classList.toggle('new', !open && lastSup > (st.seen || 0));
        if (open) render();
      }).catch(function () { /* тихо, попробуем позже */ });
  }

  function getFile(id, name) {
    fetch(API + '/file?' + q() + '&id=' + id).then(function (r) { if (!r.ok) throw 0; return r.blob(); })
      .then(function (b) { var u = URL.createObjectURL(b); var a = el('a'); a.href = u; a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(u); }, 5000); })
      .catch(function () { er.textContent = T.eNet; });
  }

  function show(v) {
    open = v; box.classList.toggle('on', v); btn.style.display = v ? 'none' : '';
    if (v) {
      idShow(); render(); btn.classList.remove('new');
      poll(true); clearInterval(timer); timer = setInterval(poll, 20000);
      setTimeout(function () { (st.consent ? ta : okb).focus(); }, 0);
    } else { clearInterval(timer); btn.focus(); }
  }

  btn.addEventListener('click', function () { show(true); });
  x.addEventListener('click', function () { show(false); });
  box.addEventListener('keydown', function (e) { if (e.key === 'Escape') show(false); });
  okb.addEventListener('click', function () { st.consent = 1; save(); idShow(); ta.focus(); });
  ab.addEventListener('click', function () { if (!st.consent) { okb.focus(); return; } er.textContent = T.shotWarn; fi.click(); });
  fi.addEventListener('change', function () {
    var f = fi.files && fi.files[0]; file = null; fname.textContent = '';
    if (!f) return;
    if (!/\.(png|jpe?g)$/i.test(f.name) || f.size > 10 * 1024 * 1024) { er.textContent = T.fileBad; fi.value = ''; return; }
    file = f; fname.textContent = T.file + ': ' + f.name; er.textContent = T.shotWarn;
  });
  ta.addEventListener('keydown', function (e) { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) form.requestSubmit ? form.requestSubmit() : sb.click(); });

  function b64(f) {
    return new Promise(function (res, rej) {
      var r = new FileReader(); r.onload = function () { res(String(r.result).split(',')[1] || ''); }; r.onerror = rej; r.readAsDataURL(f);
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!st.consent) { okb.focus(); return; }
    var text = ta.value.trim();
    if (!text && !file) return;
    if (!st.install) { st.install = rnd(24); st.key = rnd(32); save(); }
    sb.disabled = true; er.textContent = T.sending;
    (file ? b64(file) : Promise.resolve(null)).then(function (data) {
      var body = { install: st.install, key: st.key, text: text, lang: EN ? 'en' : 'ru', label: 'Сайт ' + location.pathname };
      if (data !== null) body.file = { name: file.name, data: data };
      return fetch(API + '/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (r.ok && d.ok) {
          ta.value = ''; file = null; fi.value = ''; fname.textContent = ''; er.textContent = '';
          idShow(); return poll(true);
        }
        er.textContent = r.status === 429 ? T.e429 : T.eGen;
      });
    }).catch(function () { er.textContent = T.eNet; })
      .then(function () { sb.disabled = false; });
  });

  delb.addEventListener('click', function () {
    if (!st.install || !window.confirm(T.delAsk)) return;
    fetch(API + '/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ install: st.install, key: st.key }) })
      .then(function (r) { if (!r.ok) throw 0; st = { consent: st.consent }; save(); msgs = []; last = 0; idShow(); render(); er.textContent = T.deleted; })
      .catch(function () { er.textContent = T.eNet; });
  });

  function mount() {
    document.body.appendChild(btn); document.body.appendChild(box);
    if (st.install) poll(false);
    if (location.hash === '#support') show(true);
  }
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
