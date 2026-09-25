// Page language: glossary and messages follow <html lang>.
const EN = document.documentElement.lang === 'en';
const RU = (document.documentElement.lang || '').indexOf('ru') === 0;
const UK = (document.documentElement.lang || '').indexOf('uk') === 0;

// Clock (EEST, like bimx.md top bar)
(function () {
  const el = document.getElementById('current-time');
  if (el) {
    const fmt = new Intl.DateTimeFormat('ro-RO', { timeZone: 'Europe/Chisinau', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    const tick = () => { el.textContent = fmt.format(new Date()) + ' EEST'; };
    tick(); setInterval(tick, 1000);
  }
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();

// Mobile menu
(function () {
  const btn = document.getElementById('menu-toggle');
  const nav = document.getElementById('mobile-nav');
  if (!btn || !nav) return;
  btn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
  });
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('open'); btn.setAttribute('aria-expanded', false);
  }));
})();

// Course filters
(function () {
  const buttons = document.querySelectorAll('.filters button');
  const courses = document.querySelectorAll('.course');
  buttons.forEach(b => b.addEventListener('click', () => {
    buttons.forEach(x => { x.classList.remove('active'); x.setAttribute('aria-selected', false); });
    b.classList.add('active'); b.setAttribute('aria-selected', true);
    const f = b.dataset.filter;
    courses.forEach(c => c.classList.toggle('hidden', f !== 'all' && c.dataset.level !== f));
  }));
})();

// Glossary
(function () {
  const grid = document.getElementById('glossary');
  if (!grid) return;
  const termsEn = [
    ['Admission and Maintenance Undertaking', 'Listing', 'A document in which the issuer commits to meeting its obligations while trading on BIMx; part of the admission file.'],
    ['Admission to trading', 'Listing', 'The exchange decision that allows an issuer\'s instruments to trade on one of its markets: at BIMx, the Regulated Market or the MTF.'],
    ['Agreement in Principle (MTF)', 'Listing', 'The first stage of admission to the MTF: BIMx issues it within 5 working days of receiving the complete file from the issuer and the Intermediary Participant.'],
    ['ARENA Trading', 'Infrastructure', 'The BIMx electronic trading platform, developed by the Bucharest Stock Exchange and used as SaaS.'],
    ['Bond', 'Instrument', 'A debt security in which the issuer undertakes to repay the borrowed amount plus interest (the coupon).'],
    ['Broker', 'Participant', 'An investment firm licensed by the CNPF that executes clients\' orders. Only brokers admitted as exchange members can trade on BIMx.'],
    ['Dividend', 'Return', 'The part of a company\'s net profit distributed to shareholders, usually once a year.'],
    ['ESG', 'Sustainability', 'Environmental, social and governance criteria used to assess how sustainable a company is.'],
    ['Exchange member', 'Participant', 'An investment firm licensed by the CNPF and admitted by BIMx to trade. Admission of BIMx members began on 28 September 2026.'],
    ['Exchange trader', 'Participant', 'A person certified by BIMx who enters orders into the trading system on behalf of a member broker.'],
    ['Free float', 'Indicator', 'The part of the shares actually available to the public. On the BIMx Regulated Market it must, as a rule, be at least 10%.'],
    ['Government securities (VMS)', 'Instrument', 'Debt securities issued by the Ministry of Finance. Long-term government securities are admitted to BIMx by right; treasury bills (under one year) are not.'],
    ['Green bond', 'Sustainability', 'A bond whose proceeds are used exclusively to finance projects with a positive environmental impact.'],
    ['Initiating Participant', 'Participant', 'A member broker that helps an issuer prepare and submit its file for the Regulated Market; mandatory for municipal bonds.'],
    ['Intermediary Participant', 'Participant', 'A member broker with which an issuer must have a contract on the MTF for as long as its shares are traded.'],
    ['Issuer', 'Participant', 'An entity that issues securities to raise financing on the capital market.'],
    ['Limit order', 'Trading', 'A buy or sell order executed only at a specified price or better.'],
    ['Liquidity', 'Market', 'How easily an instrument can be bought or sold without significantly moving its price.'],
    ['Listing', 'Listing', 'Admission of a company\'s securities to trading on an exchange market. The first listing on BIMx is planned by the end of 2026.'],
    ['Market capitalization', 'Indicator', 'A company\'s market value: the number of shares issued multiplied by the current share price.'],
    ['Market operator', 'Infrastructure', 'The entity authorized by the CNPF to manage and operate a capital market. In the Republic of Moldova: BIMx, authorized on 21 August 2026.'],
    ['Multilateral Trading Facility (MTF)', 'Market', 'A market run by the exchange with tailored admission and reporting requirements set by its own rules; suited to smaller companies or first-time issuers.'],
    ['Municipal bond', 'Instrument', 'A debt security issued by a local public authority. At BIMx it is admitted to the Regulated Market through an Initiating Participant.'],
    ['Portfolio', 'Investing', 'All the financial instruments held by an investor.'],
    ['Prospectus', 'Listing', 'A disclosure document describing the issuer and the offer, required for a public offer or admission to trading.'],
    ['Regulated Market', 'Market', 'The exchange market with the most complete admission, transparency and reporting requirements for issuers.'],
    ['Return', 'Return', 'The gain from an investment, usually expressed as a percentage of the amount invested.'],
    ['Share', 'Instrument', 'A security representing ownership of part of a company\'s capital, with voting rights and the right to dividends.'],
    ['Single Central Securities Depository (DCU)', 'Infrastructure', 'The institution that keeps the register of securities in the Republic of Moldova and settles trades concluded on BIMx.'],
    ['Stock index', 'Indicator', 'An indicator that tracks the prices of a representative group of listed instruments.'],
    ['T+2 settlement', 'Infrastructure', 'The actual transfer of securities and cash on the second working day after the trade, on a delivery-versus-payment basis.'],
    ['Volatility', 'Risk', 'A measure of how widely an instrument\'s price moves over a given period.']
  ];
  const termsRo = [
    ['Acțiune', 'Instrument', 'Titlu de proprietate asupra unei părți din capitalul unei companii, care oferă drept de vot și dreptul la dividende.'],
    ['Admitere la tranzacționare', 'Listare', 'Decizia bursei prin care instrumentele unui emitent pot fi tranzacționate pe una dintre piețele sale: la BIMx, Piața Reglementată sau MTF.'],
    ['Acord de principiu (MTF)', 'Listare', 'Prima etapă a admiterii pe MTF: BIMx îl eliberează în maximum 5 zile lucrătoare de la documentația completă depusă de emitent și Participantul intermediar.'],
    ['Agent de bursă', 'Participant', 'Persoana fizică atestată de BIMx care introduce ordinele în sistemul de tranzacționare, în numele unui broker membru al bursei.'],
    ['ARENA Trading', 'Infrastructură', 'Platforma electronică de tranzacționare a BIMx, dezvoltată de Bursa de Valori București și folosită în regim SaaS.'],
    ['Angajament de admitere și menținere', 'Listare', 'Document prin care emitentul își asumă respectarea obligațiilor pe durata tranzacționării la BIMx; face parte din dosarul de admitere.'],
    ['Broker', 'Participant', 'Societate de investiții licențiată de CNPF care execută ordinele clienților. La BIMx tranzacționează doar brokerii admiși ca membri ai bursei.'],
    ['Capitalizare bursieră', 'Indicator', 'Valoarea de piață a unei companii: numărul de acțiuni emise înmulțit cu prețul curent al acțiunii.'],
    ['Decontare T+2', 'Infrastructură', 'Transferul efectiv al valorilor mobiliare și al banilor, în a doua zi lucrătoare după tranzacție, după principiul livrare contra plată.'],
    ['Depozitarul Central Unic (DCU)', 'Infrastructură', 'Instituția care ține evidența valorilor mobiliare din Republica Moldova și decontează tranzacțiile încheiate la BIMx.'],
    ['Dividend', 'Randament', 'Partea din profitul net al companiei distribuită acționarilor, de regulă anual.'],
    ['Emitent', 'Participant', 'Entitatea care emite valori mobiliare pentru a atrage finanțare de pe piața de capital.'],
    ['ESG', 'Sustenabilitate', 'Criterii de mediu, sociale și de guvernanță utilizate pentru evaluarea sustenabilității unei companii.'],
    ['Indice bursier', 'Indicator', 'Indicator care reflectă evoluția prețurilor unui grup reprezentativ de instrumente listate.'],
    ['Lichiditate', 'Piață', 'Ușurința cu care un instrument poate fi cumpărat sau vândut fără a-i influența semnificativ prețul.'],
    ['Listare', 'Listare', 'Admiterea la tranzacționare a valorilor mobiliare ale unei companii pe o piață a bursei. Prima listare la BIMx este planificată până la sfârșitul anului 2026.'],
    ['Membru al bursei', 'Participant', 'Societate de investiții licențiată de CNPF și admisă de BIMx să tranzacționeze. Admiterea membrilor BIMx a început la 28 septembrie 2026.'],
    ['Free float', 'Indicator', 'Partea din acțiuni aflată efectiv la dispoziția publicului. Pe Piața Reglementată BIMx trebuie să fie, ca regulă, de cel puțin 10%.'],
    ['Obligațiune', 'Instrument', 'Titlu de creanță prin care emitentul se obligă să ramburseze suma împrumutată plus dobânda (cupon).'],
    ['Obligațiune municipală', 'Instrument', 'Titlu de creanță emis de o autoritate publică locală. La BIMx se admite pe Piața Reglementată, prin Participant inițiator.'],
    ['Obligațiune verde', 'Sustenabilitate', 'Obligațiune ale cărei fonduri sunt utilizate exclusiv pentru finanțarea proiectelor cu impact pozitiv asupra mediului.'],
    ['Operator de piață', 'Infrastructură', 'Entitatea autorizată de CNPF să administreze și să exploateze o piață de capital. În Republica Moldova: BIMx, autorizată la 21 august 2026.'],
    ['Ordin limită', 'Tranzacționare', 'Ordin de cumpărare sau vânzare executat doar la un preț specificat sau mai bun.'],
    ['Participant inițiator', 'Participant', 'Broker membru care asistă emitentul la pregătirea și depunerea dosarului pe Piața Reglementată; obligatoriu pentru obligațiunile municipale.'],
    ['Participant intermediar', 'Participant', 'Broker membru cu care emitentul are obligatoriu contract pe MTF, pe toată durata tranzacționării.'],
    ['Piața Reglementată', 'Piață', 'Piața bursei cu cele mai complete cerințe de admitere, transparență și raportare pentru emitenți.'],
    ['Portofoliu', 'Investiții', 'Totalitatea instrumentelor financiare deținute de un investitor.'],
    ['Prospect', 'Listare', 'Document de informare care prezintă emitentul și oferta, necesar pentru o ofertă publică sau admitere la tranzacționare.'],
    ['Randament', 'Randament', 'Câștigul obținut dintr-o investiție, exprimat de regulă procentual față de suma investită.'],
    ['Sistem Multilateral de Tranzacționare (MTF)', 'Piață', 'Piață administrată de bursă, cu cerințe de admitere și raportare adaptate, stabilite prin reguli proprii; potrivită companiilor mai mici sau la prima emisiune.'],
    ['Valori mobiliare de stat (VMS)', 'Instrument', 'Titluri de datorie emise de Ministerul Finanțelor. La BIMx se admit de drept VMS pe termen lung; bonurile de trezorerie (sub un an) nu.'],
    ['Volatilitate', 'Risc', 'Măsura amplitudinii variațiilor de preț ale unui instrument într-o perioadă dată.']
  ];
  const termsRu = [
    ["Акция", "Инструмент", "Ценная бумага, удостоверяющая право собственности на долю в капитале компании и дающая право голоса и право на дивиденды."],
    ["Биржевой агент", "Участник", "Физическое лицо, аттестованное BIMx, которое вводит заявки в торговую систему от имени брокера — участника биржи."],
    ["Биржевой индекс", "Показатель", "Показатель, отражающий динамику цен репрезентативной группы инструментов, прошедших листинг."],
    ["Брокер", "Участник", "Инвестиционная компания, лицензированная НКФР, которая исполняет заявки клиентов. На BIMx торгуют только брокеры, допущенные в число участников биржи."],
    ["Волатильность", "Риск", "Мера размаха колебаний цены инструмента за определённый период."],
    ["Государственные ценные бумаги (ГЦБ)", "Инструмент", "Долговые ценные бумаги, выпускаемые Министерством финансов. На BIMx по праву допускаются долгосрочные ГЦБ; казначейские векселя (сроком до года) — нет."],
    ["Дивиденд", "Доходность", "Часть чистой прибыли компании, распределяемая между акционерами, как правило ежегодно."],
    ["Допуск к торгам", "Листинг", "Решение биржи, позволяющее торговать инструментами эмитента на одном из её рынков: на BIMx — на регулируемом рынке или в MTF."],
    ["Доходность", "Доходность", "Доход от инвестиции, обычно выраженный в процентах от вложенной суммы."],
    ["Единый центральный депозитарий (ЕЦД)", "Инфраструктура", "Учреждение, которое ведёт учёт ценных бумаг в Республике Молдова и осуществляет расчёты по сделкам, заключённым на BIMx."],
    ["Зелёная облигация", "Устойчивое развитие", "Облигация, средства от размещения которой направляются исключительно на финансирование проектов с положительным воздействием на окружающую среду."],
    ["Ликвидность", "Рынок", "Лёгкость, с которой инструмент можно купить или продать без существенного влияния на его цену."],
    ["Лимитная заявка", "Торги", "Заявка на покупку или продажу, исполняемая только по указанной цене или лучше."],
    ["Листинг", "Листинг", "Допуск ценных бумаг компании к торгам на одном из рынков биржи. Первый листинг на BIMx запланирован до конца 2026 года."],
    ["Многосторонняя торговая система (MTF)", "Рынок", "Рынок, управляемый биржей, с адаптированными требованиями к допуску и отчётности, установленными собственными правилами; подходит для небольших компаний и первых выпусков."],
    ["Муниципальная облигация", "Инструмент", "Долговая ценная бумага, выпущенная органом местного публичного управления. На BIMx допускается на регулируемый рынок через участника-инициатора."],
    ["Облигация", "Инструмент", "Долговая ценная бумага, по которой эмитент обязуется вернуть заёмную сумму и выплатить проценты (купон)."],
    ["Обязательство о допуске и поддержании допуска", "Листинг", "Документ, которым эмитент обязуется соблюдать свои обязанности в течение всего периода торгов на BIMx; входит в пакет документов на допуск."],
    ["Оператор рынка", "Инфраструктура", "Организация, уполномоченная НКФР управлять рынком капитала и обеспечивать его работу. В Республике Молдова — BIMx, получившая разрешение 21 августа 2026 г."],
    ["Портфель", "Инвестиции", "Совокупность финансовых инструментов, принадлежащих инвестору."],
    ["Предварительное согласие (MTF)", "Листинг", "Первый этап допуска в MTF: BIMx выдаёт его не позднее чем через 5 рабочих дней после подачи полного пакета документов эмитентом и участником-посредником."],
    ["Проспект", "Листинг", "Информационный документ с описанием эмитента и предложения, необходимый для публичного предложения или допуска к торгам."],
    ["Расчёты T+2", "Инфраструктура", "Фактическая передача ценных бумаг и денежных средств на второй рабочий день после сделки по принципу «поставка против платежа»."],
    ["Регулируемый рынок", "Рынок", "Рынок биржи с наиболее полными требованиями к допуску, прозрачности и отчётности эмитентов."],
    ["Рыночная капитализация", "Показатель", "Рыночная стоимость компании: количество выпущенных акций, умноженное на текущую цену акции."],
    ["Участник биржи", "Участник", "Инвестиционная компания, лицензированная НКФР и допущенная BIMx к торгам. Допуск участников BIMx начинается 28 сентября 2026 г."],
    ["Участник-инициатор", "Участник", "Брокер — участник биржи, который помогает эмитенту подготовить и подать пакет документов на регулируемый рынок; обязателен для муниципальных облигаций."],
    ["Участник-посредник", "Участник", "Брокер — участник биржи, с которым эмитент в MTF обязан иметь договор на весь период торгов."],
    ["Эмитент", "Участник", "Организация, выпускающая ценные бумаги для привлечения финансирования на рынке капитала."],
    ["ARENA Trading", "Инфраструктура", "Электронная торговая платформа BIMx, разработанная Бухарестской фондовой биржей и используемая по модели SaaS."],
    ["ESG", "Устойчивое развитие", "Экологические, социальные и управленческие критерии, используемые для оценки устойчивости компании."],
    ["Free float (акции в свободном обращении)", "Показатель", "Доля акций, фактически доступная для публики. На регулируемом рынке BIMx она, как правило, должна составлять не менее 10 %."]
  ];
  const termsUk = [
    ["Акція", "Інструмент", "Цінний папір, що посвідчує право власності на частку в капіталі компанії та дає право голосу й право на дивіденди."],
    ["Багатостороння торговельна система (MTF)", "Ринок", "Ринок, яким управляє біржа, з адаптованими вимогами до допуску та звітності, установленими власними правилами; підходить для невеликих компаній і перших випусків."],
    ["Біржовий агент", "Учасник", "Фізична особа, атестована BIMx, яка вводить заявки в торговельну систему від імені брокера — учасника біржі."],
    ["Біржовий індекс", "Показник", "Показник, що відображає динаміку цін репрезентативної групи інструментів, які пройшли лістинг."],
    ["Брокер", "Учасник", "Інвестиційна компанія, ліцензована НКФР, яка виконує заявки клієнтів. На BIMx торгують лише брокери, допущені до складу учасників біржі."],
    ["Волатильність", "Ризик", "Міра розмаху коливань ціни інструмента за певний період."],
    ["Державні цінні папери (ДЦП)", "Інструмент", "Боргові цінні папери, які випускає Міністерство фінансів. На BIMx за правом допускаються довгострокові ДЦП; казначейські векселі (строком до року) — ні."],
    ["Дивіденд", "Дохідність", "Частина чистого прибутку компанії, що розподіляється між акціонерами, як правило щороку."],
    ["Допуск до торгів", "Лістинг", "Рішення біржі, яке дає змогу торгувати інструментами емітента на одному з її ринків: на BIMx — на регульованому ринку або в MTF."],
    ["Дохідність", "Дохідність", "Дохід від інвестиції, зазвичай виражений у відсотках від вкладеної суми."],
    ["Емітент", "Учасник", "Організація, яка випускає цінні папери для залучення фінансування на ринку капіталу."],
    ["Єдиний центральний депозитарій (ЄЦД)", "Інфраструктура", "Установа, яка веде облік цінних паперів у Республіці Молдова та здійснює розрахунки за угодами, укладеними на BIMx."],
    ["Зелена облігація", "Сталий розвиток", "Облігація, кошти від розміщення якої спрямовують виключно на фінансування проєктів із позитивним впливом на довкілля."],
    ["Зобов’язання щодо допуску та підтримання допуску", "Лістинг", "Документ, яким емітент зобов’язується виконувати свої обов’язки протягом усього періоду торгів на BIMx; входить до пакета документів на допуск."],
    ["Ліквідність", "Ринок", "Легкість, з якою інструмент можна купити або продати без істотного впливу на його ціну."],
    ["Лімітна заявка", "Торги", "Заявка на купівлю або продаж, яка виконується лише за вказаною або кращою ціною."],
    ["Лістинг", "Лістинг", "Допуск цінних паперів компанії до торгів на одному з ринків біржі. Перший лістинг на BIMx заплановано до кінця 2026 року."],
    ["Муніципальна облігація", "Інструмент", "Борговий цінний папір, випущений органом місцевого публічного управління. На BIMx допускається на регульований ринок через учасника-ініціатора."],
    ["Облігація", "Інструмент", "Борговий цінний папір, за яким емітент зобов’язується повернути позичену суму та сплатити відсотки (купон)."],
    ["Оператор ринку", "Інфраструктура", "Організація, уповноважена НКФР управляти ринком капіталу та забезпечувати його роботу. У Республіці Молдова — BIMx, що отримала дозвіл 21 серпня 2026 р."],
    ["Попередня згода (MTF)", "Лістинг", "Перший етап допуску до MTF: BIMx надає її не пізніше ніж через 5 робочих днів після подання повного пакета документів емітентом і учасником-посередником."],
    ["Портфель", "Інвестиції", "Сукупність фінансових інструментів, що належать інвесторові."],
    ["Проспект", "Лістинг", "Інформаційний документ з описом емітента та пропозиції, необхідний для публічної пропозиції або допуску до торгів."],
    ["Регульований ринок", "Ринок", "Ринок біржі з найповнішими вимогами до допуску, прозорості та звітності емітентів."],
    ["Ринкова капіталізація", "Показник", "Ринкова вартість компанії: кількість випущених акцій, помножена на поточну ціну акції."],
    ["Розрахунки T+2", "Інфраструктура", "Фактична передача цінних паперів і коштів на другий робочий день після угоди за принципом «поставка проти платежу»."],
    ["Учасник біржі", "Учасник", "Інвестиційна компанія, ліцензована НКФР і допущена BIMx до торгів. Допуск учасників BIMx розпочинається 28 вересня 2026 р."],
    ["Учасник-ініціатор", "Учасник", "Брокер — учасник біржі, який допомагає емітенту підготувати та подати пакет документів на регульований ринок; обов’язковий для муніципальних облігацій."],
    ["Учасник-посередник", "Учасник", "Брокер — учасник біржі, з яким емітент у MTF зобов’язаний мати договір протягом усього періоду торгів."],
    ["ARENA Trading", "Інфраструктура", "Електронна торговельна платформа BIMx, розроблена Бухарестською фондовою біржею та використовувана за моделлю SaaS."],
    ["ESG", "Сталий розвиток", "Екологічні, соціальні та управлінські критерії, які використовують для оцінки сталості компанії."],
    ["Free float (акції у вільному обігу)", "Показник", "Частка акцій, фактично доступна для публіки. На регульованому ринку BIMx вона, як правило, має становити щонайменше 10 %."]
  ];
  const terms = EN ? termsEn : RU ? termsRu : UK ? termsUk : termsRo;
  const empty = document.getElementById('gloss-empty');
  const input = document.getElementById('gloss-search');
  const lettersEl = document.getElementById('letters');
  const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  let letter = null;

  grid.innerHTML = terms.map(([t, c, d]) =>
    `<article class="term" data-t="${norm(t)}" data-d="${norm(d)}"><h4>${t}<small>${c}</small></h4><p>${d}</p></article>`
  ).join('');

  const letters = [...new Set(terms.map(t => norm(t[0])[0].toUpperCase()))];
  lettersEl.innerHTML = [EN ? 'All' : RU ? 'Все' : UK ? 'Усі' : 'Toate', ...letters].map((l, i) =>
    `<button data-l="${i ? l : ''}" class="${i ? '' : 'active'}" style="${i ? '' : 'width:auto;padding:0 12px'}">${l}</button>`
  ).join('');

  function apply() {
    const q = norm(input.value.trim());
    let shown = 0;
    grid.querySelectorAll('.term').forEach(el => {
      const ok = (!q || el.dataset.t.includes(q) || el.dataset.d.includes(q)) &&
                 (!letter || el.dataset.t[0].toUpperCase() === letter);
      el.classList.toggle('hidden', !ok);
      if (ok) shown++;
    });
    empty.classList.toggle('show', shown === 0);
  }
  input.addEventListener('input', apply);
  lettersEl.addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    lettersEl.querySelectorAll('button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    letter = b.dataset.l || null;
    apply();
  });
})();

// Newsletter (demo)
(function () {
  const form = document.getElementById('newsletter-form');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const input = form.querySelector('input');
    const msg = document.getElementById('newsletter-msg');
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value);
    msg.style.display = 'block';
    msg.style.color = valid ? '#6ee0a8' : '#ff8a8a';
    msg.textContent = valid
      ? (EN ? 'Check your inbox or spam folder to confirm your subscription.' : RU ? 'Проверьте папку «Входящие» или «Спам», чтобы подтвердить подписку.' : UK ? 'Перевірте теки «Вхідні» або «Спам», щоб підтвердити підписку.' : 'Verifică-ți dosarul de intrări sau spam pentru a-ți confirma abonarea.')
      : (EN ? 'Please enter a valid email address.' : RU ? 'Введите корректный адрес электронной почты.' : UK ? 'Введіть коректну адресу електронної пошти.' : 'Te rugăm să introduci o adresă de email validă.');
    if (valid) input.value = '';
  });
})();

// Reveal on scroll + active section nav
(function () {
  const io = new IntersectionObserver(entries => entries.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
  }), { threshold: .12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  const nav = document.getElementById('section-nav');
  if (!nav) return;
  const links = nav.querySelectorAll('a');
  const map = new Map([...links].map(a => [a.getAttribute('href').slice(1), a]));
  const spy = new IntersectionObserver(entries => entries.forEach(en => {
    if (en.isIntersecting) {
      links.forEach(l => l.classList.remove('active'));
      const a = map.get(en.target.id);
      if (a) { a.classList.add('active'); nav.scrollLeft = a.offsetLeft - nav.clientWidth / 2 + a.offsetWidth / 2; }
    }
  }), { rootMargin: '-45% 0px -50% 0px' });
  map.forEach((_, id) => { const s = document.getElementById(id); if (s) spy.observe(s); });
})();
