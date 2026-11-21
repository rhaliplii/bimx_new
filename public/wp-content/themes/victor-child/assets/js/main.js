jQuery(function ($) {
    $(document).ready(function () {

        $(document).on('click', function (e) {
            if (!$(e.target).closest('.close, .burger, .primary-navigation').length) {
                $('.primary-navigation').removeClass('active');
            }
        });


        $('.burger').on('click', function () {
            $('header .center').slideToggle()
            $(this).toggleClass('active')
        })


        $(window).on('scroll', function () {
            if ($(this).scrollTop() > 0) {
                $('header').addClass('scrolled');
            } else {
                $('header').removeClass('scrolled');
            }
        });

        $('.partners').slick({
            slidesToShow: 8,
            slidesToScroll: 1,
            dots: false,
            arrows: false,
            autoplay: true,
            infinite: true,
            responsive: [{
                breakpoint: 768, settings: {
                    slidesToShow: 2.5, infinite: false,
                }
            }]
        })

        $('.header_content .search').on('click', function () {
            $('.modal_search_form').addClass('active')
        })
        $('.modal_search_form .close').on('click', function () {
            $('.modal_search_form').removeClass('active')
        })

        $('.member button').on('click', function () {
            $(this).closest('.member').find('.modal_overlay').fadeIn()
        })

        $('.modal_content_member .close').on('click', function () {
            $(this).closest('.modal_overlay').fadeOut()
        })

        $('.stakeholder .head_section').on('click', function () {
            $(this).closest('.stakeholder').find('.benefits_accordion').slideToggle()
        })

        // Contact modal
        $('a[href="#open_contact_modal"]').on('click', function () {
            $('.contact_modal_overlay').addClass('active')
        })
        $('.modal_content .close').on('click', function () {
            $('.contact_modal_overlay').removeClass('active')
        })

        $('.not_click').on('click', function () {
            $(this).find('ul.sub-menu').slideToggle()
        })

        // Back to main menu on mobile
        $(document).ready(function () {

            // 1. Deschidere / Toggle submeniu la click pe părinte
            // $('.primary-navigation ul li.menu-item-has-children').on('click', function (e) {
            //     // Dacă s-a dat click direct pe butonul de înapoi, lăsăm funcția de mobile să se ocupe
            //     if ($(e.target).closest('.back_to_main_menu').length) {
            //         return;
            //     }
            //
            //     e.stopPropagation();
            //
            //     let curentSubMenu = $(this).find('> ul.sub-menu');
            //
            //     if (curentSubMenu.hasClass('active')) {
            //         curentSubMenu.removeClass('active');
            //     } else {
            //         $('ul.sub-menu').removeClass('active');
            //         curentSubMenu.addClass('active');
            //     }
            // });

            $('.primary-navigation ul li.menu-item-has-children').on('click', function (e) {
                // 1. Dacă s-a dat click direct pe butonul de înapoi, lăsăm funcția de mobile să se ocupe
                if ($(e.target).closest('.back_to_main_menu').length) {
                    return;
                }

                // 2. REZOLVAREA PROBLEMEI: Prevenim închiderea dacă dăm click în interiorul sub-meniului
                // Dacă elementul pe care am dat click se află deja în sub-meniul vizat de acest LI, ne oprim.
                if ($(e.target).closest('.sub-menu').parent().is(this)) {
                    return; // lăsăm click-ul să își vadă de treabă (ex: te duce pe link-ul copil)
                }

                e.stopPropagation();

                let curentSubMenu = $(this).find('> ul.sub-menu');

                if (curentSubMenu.hasClass('active')) {
                    curentSubMenu.removeClass('active');
                } else {
                    // 3. CORELARE: Închidem DOAR sub-meniurile "surori" (de la același nivel).
                    // Nu folosim selectorul global care ar închide și meniurile părinte.
                    $(this).siblings().find('> ul.sub-menu').removeClass('active');

                    curentSubMenu.addClass('active');
                }
            });

            // 2. FUNCȚIONAL MOBILE: Click pe butonul "Înapoi" din interiorul submeniului
            $('.primary-navigation').on('click', '.back_to_main_menu', function (e) {
                e.stopPropagation(); // Oprim propagarea ca să nu declanșăm click-ul părintelui (punctul 1)

                // Găsim submeniul în care se află butonul pe care s-a dat click și îi ștergem clasa
                $(this).closest('ul.sub-menu').removeClass('active');
            });

            // 3. Închiderea meniului când se dă click oriunde în afara lui
            $(document).on('click', function (e) {
                if (!$(e.target).closest('.primary-navigation').length) {
                    $('ul.sub-menu').removeClass('active');
                }
            });

        });


    })
})


function formatLargeNumber(num) {
    if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B';
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    return num.toLocaleString();
}

// Top gainer tabel
let summaryData = {gainers: [], losers: [], most_traded: []};

async function loadMarketSummary() {
    try {
        const response = await fetch('/wp-admin/admin-ajax.php?action=get_market_summary');
        const data = await response.json();
        // Salvăm datele primite în variabila globală
        summaryData = data;
        // Afișăm implicit primul tab
        switchSummary('gainers');
    } catch (e) {
        console.error("Eroare la încărcarea datelor de piață:", e);
    }
}

function switchSummary(type) {

    // 1. Schimbăm aspectul butoanelor (clasa active)
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        // Verificăm ce buton a fost apăsat după text sau argument
        if (btn.innerText.toLowerCase().includes(type.replace('_', ' '))) {
            btn.classList.add('active');
        }
    });

    const tbody = document.getElementById('market-table-body');
    if (!tbody) return;
    const items = summaryData[type] || [];

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Nu există date disponibile pentru această categorie.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map((item, index) => {
        // Securizare date: dacă o valoare lipsește, punem 0
        const price = Number(item.price || 0);
        const pct = Number(item.pct || 0);
        const volume = Number(item.volume || 0);
        const mcap = Number(item.market_cap || 0);
        const isPos = pct > 0;
        const isNeg = pct < 0;
        const colorClass = isPos ? 'pos' : (isNeg ? 'neg' : '');
        const rowNumber = index + 1;
        return `
            <tr>
                <td>
                    <span class="number">
                     ${rowNumber}
                     </span>
                </td>
                <td>
                    <div class="symbol-cell">
                        <span class="symbol-name">${item.symbol}</span>
                    </div>
                </td>
                <td>
                        <span class="full-name">${item.name}</span>
               </td>
                <td style="font-weight: 600;">
                    <span class="price">
                    ${price}
                    </span>
                </td>
                <td>
                    <span class="pct-badge ${colorClass}">
                      ${isPos ? '+' : ''}${pct.toFixed(2)}%
                    </span>
                </td>
                <td style="color: #64748b;">${volume.toLocaleString('ro-RO')}</td>
                <td style="color: #64748b;">${formatLargeNumber(mcap)}</td>
                
            </tr>
        `;
    }).join('');
}

function formatLargeNumber(num) {
    const n = Number(num || 0);
    if (n >= 1000000000) return (n / 1000000000).toFixed(2) + 'B';
    if (n >= 1000000) return (n / 1000000).toFixed(2) + 'M';
    return n.toLocaleString('ro-RO');
}

document.addEventListener('DOMContentLoaded', loadMarketSummary);


async function initTickerBar() {
    try {
        const response = await fetch('/wp-admin/admin-ajax.php?action=get_bimx_movers&full_list=yes');

        let stocks = await response.json();

        stocks = stocks.slice(0, 10);

        const tickerContainer = document.getElementById('bimx-ticker-content');
        if (!tickerContainer) return;

        // Generăm HTML-ul pentru un set de date
        const tickerHTML = stocks.map(s => {
            const isPos = parseFloat(s.change) >= 0;
            const prefix = isPos ? '+' : '';
            return `
                <div class="ticker-item">
                    <span class="t-symbol">${s.symbol}</span>
                    <span class="t-price">${parseFloat(s.price).toFixed(2)}</span>
                    <span class="t-pct ${isPos ? 'pos' : 'neg'}">${prefix}${s.percent_change}%</span>
                </div>
            `;
        }).join('');

        // Injectăm lista de două ori pentru a asigura continuitatea animației
        tickerContainer.innerHTML = tickerHTML + tickerHTML;

    } catch (e) {
        console.error("Eroare la încărcarea ticker-ului:", e);
    }
}

// Pornim ticker-ul
document.addEventListener('DOMContentLoaded', initTickerBar);


// Copy article url
document.addEventListener('DOMContentLoaded', function () {
    const copyBtn = document.getElementById('copy-link-btn');

    if (copyBtn) {
        copyBtn.addEventListener('click', function () {
            const urlToCopy = this.getAttribute('data-link');

            // Folosim API-ul modern de clipboard
            navigator.clipboard.writeText(urlToCopy).then(() => {
                // Adăugăm o clasă care activează stilul de tooltip vizual
                copyBtn.classList.add('copied');

                // Eliminăm mesajul după 2 secunde
                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Eroare la copierea link-ului: ', err);
            });
        });
    }
});