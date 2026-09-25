"""Organigrama BIMx (pagina organigrama/), redată în HTML după PDF-ul oficial „Organigrama-Final.pdf”.

Structura și notele sunt cele din PDF (conform Statutului BIM, Cap. V, Art. 22–44, și Legii nr. 171/2012).
"""

T = {
    "ro": {
        "title": "Bursa Internațională a Moldovei S.A.",
        "sub": "Organigrama corporativă · conform Statutului BIM (Cap. V, Art. 22–44) și Legii nr. 171/2012",
        "aga": "Adunarea Generală a Acționarilor", "cenzori": "Comisia de cenzori", "audit_ext": "Audit extern",
        "consiliu": "Consiliul Bursei", "audit_int": "Audit intern", "arbitraj": "Arbitrajul BIM",
        "ceo": ("Președinte", "CEO"), "deputy": ("Vicepreședinte", "Deputy CEO"),
        "ceo_deps": ["Departament Conformitate și Risc", "Departament Administrativ"],
        "deputy_deps": ["Departament Listing și Operațiuni", "Departament IT", "Departament Supravegherea pieței"],
        "dashed": "raportare operațională",
        "note": "<strong>Notă:</strong> Auditul intern raportează <em>funcțional Consiliului Bursei</em> și <em>operațional CEO-ului</em> "
                "(linie punctată). Conducătorii coordonează în mod comun activitatea zilnică, deciziile fiind luate prin "
                "consimțământul ambilor (Art. 42 alin. 8–10).",
        "legend_solid": "subordonare", "legend_dashed": "raportare operațională",
    },
    "en": {
        "title": "Moldova International Stock Exchange S.A.",
        "sub": "Corporate organisational chart · under the BIM Articles of Association (Ch. V, Art. 22–44) and Law No. 171/2012",
        "aga": "General Meeting of Shareholders", "cenzori": "Audit Committee", "audit_ext": "External audit",
        "consiliu": "Exchange Council", "audit_int": "Internal audit", "arbitraj": "BIM Arbitration",
        "ceo": ("President", "CEO"), "deputy": ("Vice-President", "Deputy CEO"),
        "ceo_deps": ["Compliance and Risk Department", "Administrative Department"],
        "deputy_deps": ["Listing and Operations Department", "IT Department", "Market Surveillance Department"],
        "dashed": "operational reporting",
        "note": "<strong>Note:</strong> Internal audit reports <em>functionally to the Exchange Council</em> and <em>operationally to the CEO</em> "
                "(dotted line). The executives jointly coordinate day-to-day activity, with decisions taken with the consent "
                "of both (Art. 42(8)–(10)).",
        "legend_solid": "reporting line", "legend_dashed": "operational reporting",
    },
}


def _box(text, cls):
    return f'<div class="bx-org-box {cls}">{text}</div>'


def org_chart(lang):
    t = T[lang]
    ceo = f'{t["ceo"][0]}<small>{t["ceo"][1]}</small>'
    dep = f'{t["deputy"][0]}<small>{t["deputy"][1]}</small>'
    deps = lambda items: "".join(f'<li>{_box(x, "is-dept")}</li>' for x in items)
    return f'''
<figure class="bx-org" aria-label="{t["title"]}">
  <figcaption><strong>{t["title"]}</strong><span>{t["sub"]}</span></figcaption>
  <div class="bx-org-tier bx-org-t1">{_box(t["cenzori"], "is-side")}{_box(t["aga"], "is-gov")}{_box(t["audit_ext"], "is-side")}</div>
  <div class="bx-org-tier bx-org-t2">{_box(t["audit_int"], "is-audit")}{_box(t["consiliu"], "is-gov")}{_box(t["arbitraj"], "is-side")}</div>
  <div class="bx-org-exec">
    <div class="bx-org-branch">{_box(ceo, "is-exec is-ceo")}<ul class="bx-org-deps">{deps(t["ceo_deps"])}</ul></div>
    <div class="bx-org-branch">{_box(dep, "is-exec")}<ul class="bx-org-deps">{deps(t["deputy_deps"])}</ul></div>
  </div>
  <p class="bx-org-legend"><span class="is-solid"></span>{t["legend_solid"]}<span class="is-dashed"></span>{t["legend_dashed"]}</p>
  <p class="bx-org-note">{t["note"]}</p>
</figure>'''
