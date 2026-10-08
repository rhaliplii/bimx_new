# -*- coding: utf-8 -*-
"""Conținutul paginilor „Politica de confidențialitate” și „Politica cookie” (fixes.PAGES, kind „text”).

Descrie ce face site-ul în realitate (verificat la 08.10.2026): fără analytics, publicitate sau scripturi de rețele sociale;
fonturile găzduite local; harta Google încărcată doar la clic; un cookie propriu (ds-popup-1) și o cheie localStorage
(bimx-academy-progress). Textul juridic trebuie confirmat de BIMx înainte de publicarea pe bimx.md.
"""

UPDATED = {"ro": "8 octombrie 2026", "en": "8 October 2026", "ru": "8 октября 2026 г.", "uk": "8 жовтня 2026 р."}

LEAD = {
    "politica-de-confidentialitate": {
        "ro": "Cum tratează site-ul BIMx datele dumneavoastră personale.",
        "en": "How the BIMx website handles your personal data.",
        "ru": "Как сайт BIMx обращается с вашими персональными данными.",
        "uk": "Як сайт BIMx поводиться з вашими персональними даними.",
    },
    "politica-cookie": {
        "ro": "Ce cookie-uri și ce date stocate în browser folosește site-ul BIMx.",
        "en": "Which cookies and browser storage the BIMx website uses.",
        "ru": "Какие файлы cookie и данные в браузере использует сайт BIMx.",
        "uk": "Які файли cookie та дані в браузері використовує сайт BIMx.",
    },
}

_CONTACT = {
    "ro": ("Bursa Internațională a Moldovei S.A. (BIMx), IDNO 1025600073907, str. Vlaicu Pârcălab 63, MD-2012, Chișinău, Republica Moldova"),
    "en": ("Moldova International Stock Exchange JSC (BIMx), IDNO 1025600073907, 63 Vlaicu Pârcălab St., MD-2012, Chișinău, Republic of Moldova"),
    "ru": ("АО «Международная фондовая биржа Молдовы» (BIMx), IDNO 1025600073907, ул. Влайку Пыркэлаб, 63, MD-2012, Кишинэу, Республика Молдова"),
    "uk": ("АТ «Міжнародна фондова біржа Молдови» (BIMx), IDNO 1025600073907, вул. Влайку Пиркелаб, 63, MD-2012, Кишинеу, Республіка Молдова"),
}
_MAIL = '<a href="mailto:office@bimx.md">office@bimx.md</a>'


def privacy(lang, link):
    cookie = link("politica-cookie/index.html")
    c = _CONTACT[lang]
    if lang == "ro":
        return f"""
<h2>Cine răspunde de date</h2>
<p>{c}. Pentru orice întrebare despre datele dumneavoastră: {_MAIL}, +373 22 89 77 00.</p>
<h2>Ce date colectează site-ul</h2>
<p>Site-ul nu folosește instrumente de analiză a traficului, publicitate sau scripturi ale rețelelor sociale și nu creează
profiluri ale vizitatorilor. Linkurile spre Facebook, LinkedIn și X sunt simple trimiteri; acele platforme nu primesc date
până nu le deschideți.</p>
<ul>
<li><strong>Formularul de contact:</strong> numele, adresa de e-mail, telefonul, subiectul și mesajul, folosite doar pentru a
răspunde solicitării. În versiunea actuală a site-ului formularul nu trimite date; pentru solicitări scrieți la {_MAIL}.</li>
<li><strong>Date tehnice:</strong> furnizorul de găzduire poate înregistra adresa IP și momentul accesării, pentru securitatea
și funcționarea site-ului.</li>
</ul>
<h2>Servicii ale altor companii</h2>
<ul>
<li><strong>Fonturile</strong> site-ului sunt găzduite împreună cu site-ul; browserul nu contactează Google Fonts.</li>
<li><strong>Harta Google Maps</strong> de pe pagina Contacte se încarcă numai după ce apăsați „Afișați harta”. Abia atunci
browserul contactează Google, care poate seta cookie-uri conform propriei politici.</li>
</ul>
<h2>Cookie-uri</h2>
<p>Lista completă a cookie-urilor și a datelor stocate în browser se află în <a href="{cookie}">Politica cookie</a>.</p>
<h2>Drepturile dumneavoastră</h2>
<p>Puteți cere accesul la datele dumneavoastră, corectarea sau ștergerea lor și vă puteți opune prelucrării, scriind la
{_MAIL}. Aveți dreptul să depuneți o plângere la Centrul Național pentru Protecția Datelor cu Caracter Personal.</p>
<p class="bx-legal-date">Ultima actualizare: {UPDATED[lang]}</p>"""
    if lang == "en":
        return f"""
<h2>Who is responsible for your data</h2>
<p>{c}. For any question about your data: {_MAIL}, +373 22 89 77 00.</p>
<h2>What data the website collects</h2>
<p>The website uses no traffic analytics, advertising or social media scripts and does not build visitor profiles. The links to
Facebook, LinkedIn and X are plain links; those platforms receive no data until you open them.</p>
<ul>
<li><strong>Contact form:</strong> your name, email address, phone number, subject and message, used only to answer your request.
In the current version of the website the form does not send any data; please write to {_MAIL}.</li>
<li><strong>Technical data:</strong> the hosting provider may log your IP address and the time of access, for the security and
operation of the website.</li>
</ul>
<h2>Services of other companies</h2>
<ul>
<li><strong>Fonts</strong> are hosted together with the website; your browser does not contact Google Fonts.</li>
<li><strong>The Google Maps map</strong> on the Contacts page loads only after you click “Show the map”. Only then does your
browser contact Google, which may set cookies under its own policy.</li>
</ul>
<h2>Cookies</h2>
<p>The full list of cookies and browser storage is in the <a href="{cookie}">Cookie policy</a>.</p>
<h2>Your rights</h2>
<p>You may request access to your data, its correction or erasure, and object to its processing by writing to {_MAIL}. You have
the right to lodge a complaint with the National Center for Personal Data Protection of the Republic of Moldova.</p>
<p class="bx-legal-date">Last updated: {UPDATED[lang]}</p>"""
    if lang == "ru":
        return f"""
<h2>Кто отвечает за данные</h2>
<p>{c}. По любым вопросам о ваших данных: {_MAIL}, +373 22 89 77 00.</p>
<h2>Какие данные собирает сайт</h2>
<p>Сайт не использует инструменты веб-аналитики, рекламу или скрипты социальных сетей и не создаёт профили посетителей. Ссылки на
Facebook, LinkedIn и X — обычные ссылки; эти платформы не получают данных, пока вы их не откроете.</p>
<ul>
<li><strong>Форма обратной связи:</strong> имя, адрес электронной почты, телефон, тема и сообщение — только для ответа на
запрос. В текущей версии сайта форма не отправляет данные; пишите на {_MAIL}.</li>
<li><strong>Технические данные:</strong> хостинг-провайдер может регистрировать IP-адрес и время доступа для безопасности и
работы сайта.</li>
</ul>
<h2>Сервисы других компаний</h2>
<ul>
<li><strong>Шрифты</strong> размещены вместе с сайтом; браузер не обращается к Google Fonts.</li>
<li><strong>Карта Google Maps</strong> на странице «Контакты» загружается только после нажатия «Показать карту». Только тогда
браузер обращается к Google, который может устанавливать файлы cookie согласно своей политике.</li>
</ul>
<h2>Файлы cookie</h2>
<p>Полный перечень файлов cookie и данных в браузере — в <a href="{cookie}">Политике использования файлов cookie</a>.</p>
<h2>Ваши права</h2>
<p>Вы можете запросить доступ к своим данным, их исправление или удаление и возразить против их обработки, написав на {_MAIL}.
Вы вправе подать жалобу в Национальный центр по защите персональных данных Республики Молдова.</p>
<p class="bx-legal-date">Последнее обновление: {UPDATED[lang]}</p>"""
    return f"""
<h2>Хто відповідає за дані</h2>
<p>{c}. З будь-яких питань щодо ваших даних: {_MAIL}, +373 22 89 77 00.</p>
<h2>Які дані збирає сайт</h2>
<p>Сайт не використовує інструменти веб-аналітики, рекламу чи скрипти соціальних мереж і не створює профілі відвідувачів.
Посилання на Facebook, LinkedIn і X — звичайні посилання; ці платформи не отримують даних, доки ви їх не відкриєте.</p>
<ul>
<li><strong>Форма зворотного зв’язку:</strong> ім’я, адреса електронної пошти, телефон, тема й повідомлення — лише для відповіді
на запит. У поточній версії сайту форма не надсилає даних; пишіть на {_MAIL}.</li>
<li><strong>Технічні дані:</strong> хостинг-провайдер може реєструвати IP-адресу й час доступу для безпеки та роботи сайту.</li>
</ul>
<h2>Сервіси інших компаній</h2>
<ul>
<li><strong>Шрифти</strong> розміщено разом із сайтом; браузер не звертається до Google Fonts.</li>
<li><strong>Карта Google Maps</strong> на сторінці «Контакти» завантажується лише після натискання «Показати карту». Лише тоді
браузер звертається до Google, який може встановлювати файли cookie відповідно до своєї політики.</li>
</ul>
<h2>Файли cookie</h2>
<p>Повний перелік файлів cookie та даних у браузері — у <a href="{cookie}">Політиці щодо файлів cookie</a>.</p>
<h2>Ваші права</h2>
<p>Ви можете попросити доступ до своїх даних, їх виправлення чи видалення та заперечити проти їх обробки, написавши на {_MAIL}.
Ви маєте право подати скаргу до Національного центру захисту персональних даних Республіки Молдова.</p>
<p class="bx-legal-date">Останнє оновлення: {UPDATED[lang]}</p>"""


_TABLE_HEAD = {
    "ro": ("Nume", "Tip", "Rol", "Durată"),
    "en": ("Name", "Type", "Purpose", "Duration"),
    "ru": ("Название", "Тип", "Назначение", "Срок"),
    "uk": ("Назва", "Тип", "Призначення", "Строк"),
}
_ROWS = {
    "ro": [("ds-popup-1", "Cookie propriu, funcțional", "Ține minte că ați închis avertizarea despre datele demonstrative, ca să nu reapară la fiecare pagină.", "1 zi"),
           ("bimx-academy-progress", "Stocare locală (localStorage), funcțională", "Lecțiile BIMx Academy parcurse. Rămâne doar în browserul dumneavoastră, nu este trimisă nicăieri.", "Până o ștergeți")],
    "en": [("ds-popup-1", "First-party cookie, functional", "Remembers that you closed the demo-data notice, so it does not reappear on every page.", "1 day"),
           ("bimx-academy-progress", "Local storage, functional", "The BIMx Academy lessons you have completed. It stays in your browser and is never sent anywhere.", "Until you delete it")],
    "ru": [("ds-popup-1", "Собственный cookie, функциональный", "Запоминает, что вы закрыли уведомление о демонстрационных данных, чтобы оно не появлялось на каждой странице.", "1 день"),
           ("bimx-academy-progress", "Локальное хранилище, функциональное", "Пройденные уроки BIMx Academy. Остаётся только в вашем браузере и никуда не передаётся.", "Пока вы его не удалите")],
    "uk": [("ds-popup-1", "Власний cookie, функціональний", "Запам’ятовує, що ви закрили повідомлення про демонстраційні дані, щоб воно не з’являлося на кожній сторінці.", "1 день"),
           ("bimx-academy-progress", "Локальне сховище, функціональне", "Пройдені уроки BIMx Academy. Залишається лише у вашому браузері й нікуди не передається.", "Доки ви його не видалите")],
}


def cookies(lang, link):
    privacy_link = link("politica-de-confidentialitate/index.html")
    h = _TABLE_HEAD[lang]
    rows = "".join(f"<tr><td><code>{n}</code></td><td>{t}</td><td>{r}</td><td>{d}</td></tr>" for n, t, r, d in _ROWS[lang])
    table = (f'<div class="bx-legal-table"><table><thead><tr><th>{h[0]}</th><th>{h[1]}</th><th>{h[2]}</th><th>{h[3]}</th></tr></thead>'
             f"<tbody>{rows}</tbody></table></div>")
    if lang == "ro":
        return f"""
<h2>Ce sunt cookie-urile</h2>
<p>Cookie-urile sunt fișiere mici pe care un site le salvează în browser. Site-ul BIMx folosește doar cookie-uri și date
stocate în browser care îi sunt necesare pentru a funcționa așa cum ați ales. Nu folosește cookie-uri de analiză, publicitate
sau ale rețelelor sociale, de aceea nu vă cere acordul printr-un banner.</p>
<h2>Ce folosește site-ul</h2>
{table}
<h2>Cookie-urile altor companii</h2>
<p>Harta Google Maps de pe pagina Contacte se încarcă numai după ce apăsați „Afișați harta”. Din acel moment, Google poate
seta cookie-uri proprii, descrise în politica de confidențialitate Google. Fonturile site-ului sunt găzduite împreună cu
site-ul, fără cereri către Google Fonts.</p>
<h2>Cum le ștergeți</h2>
<p>Puteți șterge sau bloca oricând cookie-urile și datele stocate din setările browserului. Site-ul funcționează și fără ele;
doar avertizarea despre date și progresul la lecții nu vor mai fi memorate.</p>
<p>Dacă site-ul va folosi pe viitor cookie-uri care nu sunt necesare, de exemplu pentru statistici, vă vom cere acordul înainte
de a le seta. Despre datele personale: <a href="{privacy_link}">Politica de confidențialitate</a>.</p>
<p class="bx-legal-date">Ultima actualizare: {UPDATED[lang]}</p>"""
    if lang == "en":
        return f"""
<h2>What cookies are</h2>
<p>Cookies are small files a website saves in your browser. The BIMx website uses only cookies and browser storage it needs to
work the way you chose. It uses no analytics, advertising or social media cookies, which is why it does not ask for your
consent with a banner.</p>
<h2>What the website uses</h2>
{table}
<h2>Cookies of other companies</h2>
<p>The Google Maps map on the Contacts page loads only after you click “Show the map”. From that moment, Google may set its own
cookies, described in Google's privacy policy. The website's fonts are hosted together with the website, with no requests
to Google Fonts.</p>
<h2>How to delete them</h2>
<p>You can delete or block cookies and stored data at any time in your browser settings. The website works without them; only
the data notice and your lesson progress will no longer be remembered.</p>
<p>If the website ever uses cookies that are not necessary, for example for statistics, we will ask for your consent before
setting them. About personal data: <a href="{privacy_link}">Privacy policy</a>.</p>
<p class="bx-legal-date">Last updated: {UPDATED[lang]}</p>"""
    if lang == "ru":
        return f"""
<h2>Что такое файлы cookie</h2>
<p>Файлы cookie — небольшие файлы, которые сайт сохраняет в браузере. Сайт BIMx использует только те файлы cookie и данные в
браузере, которые нужны ему для работы так, как вы выбрали. Он не использует аналитические, рекламные файлы cookie или cookie
социальных сетей, поэтому не запрашивает согласие с помощью баннера.</p>
<h2>Что использует сайт</h2>
{table}
<h2>Файлы cookie других компаний</h2>
<p>Карта Google Maps на странице «Контакты» загружается только после нажатия «Показать карту». С этого момента Google может
устанавливать собственные файлы cookie, описанные в политике конфиденциальности Google. Шрифты сайта размещены вместе с
сайтом, без обращений к Google Fonts.</p>
<h2>Как их удалить</h2>
<p>Вы можете в любой момент удалить или заблокировать файлы cookie и сохранённые данные в настройках браузера. Сайт работает и
без них; только уведомление о данных и прогресс по урокам больше не будут запоминаться.</p>
<p>Если в будущем сайт будет использовать необязательные файлы cookie, например для статистики, мы запросим ваше согласие до их
установки. О персональных данных: <a href="{privacy_link}">Политика конфиденциальности</a>.</p>
<p class="bx-legal-date">Последнее обновление: {UPDATED[lang]}</p>"""
    return f"""
<h2>Що таке файли cookie</h2>
<p>Файли cookie — невеликі файли, які сайт зберігає в браузері. Сайт BIMx використовує лише ті файли cookie та дані в браузері,
що потрібні йому для роботи так, як ви обрали. Він не використовує аналітичні, рекламні файли cookie чи cookie соціальних
мереж, тому не просить згоди за допомогою банера.</p>
<h2>Що використовує сайт</h2>
{table}
<h2>Файли cookie інших компаній</h2>
<p>Карта Google Maps на сторінці «Контакти» завантажується лише після натискання «Показати карту». Відтоді Google може
встановлювати власні файли cookie, описані в політиці конфіденційності Google. Шрифти сайту розміщено разом із сайтом, без
звернень до Google Fonts.</p>
<h2>Як їх видалити</h2>
<p>Ви можете будь-коли видалити чи заблокувати файли cookie та збережені дані в налаштуваннях браузера. Сайт працює й без них;
лише повідомлення про дані та прогрес уроків більше не запам’ятовуватимуться.</p>
<p>Якщо в майбутньому сайт використовуватиме необов’язкові файли cookie, наприклад для статистики, ми попросимо вашої згоди до
їх встановлення. Про персональні дані: <a href="{privacy_link}">Політика конфіденційності</a>.</p>
<p class="bx-legal-date">Останнє оновлення: {UPDATED[lang]}</p>"""


def legal_html(key, lang, link):
    return privacy(lang, link) if key == "politica-de-confidentialitate" else cookies(lang, link)
