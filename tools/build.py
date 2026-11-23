#!/usr/bin/env python3
"""
Builds the whole site from this one file.

  python3 tools/build.py

It writes every .html page and js/i18n.js (the Spanish text). The English text sits in the
pages themselves, so the site works even if JavaScript is off. Every text that has a Spanish
version is written once below, as a pair: English first, Spanish second.

To change a sentence: edit it here (both languages), run the script, then commit the files it
changed. Do not edit the .html files by hand, the next build would overwrite the changes.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import ICONS   # tile colours live next to the drawings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "20261123e"      # change it whenever css/styles.css or a .js file changes
YEAR = "2026"
NAME = "Miguel Lopez"
ES = {}                    # key -> Spanish text, written to js/i18n.js
_n = {}
PAGE = ""


def esc(s):
    return html.escape(s, quote=False)


def escq(s):
    return html.escape(s, quote=True)


def _key(key):
    if key:
        return key
    _n[PAGE] = _n.get(PAGE, 0) + 1
    return "%s.%d" % (PAGE, _n[PAGE])


# Names of companies, schools and people. They are never translated, so they are wrapped in
# translate="no": a browser's own translator then leaves them alone too ("Baker Hughes" must not
# become "Panadero Hughes").
PROTECT = ["Wellbore Integrity Solutions", "Nabors Drilling International", "Nabors Drilling Solutions",
           "Smith International", "Baker Hughes", "Schlumberger", "Roku Tech", "Nabors", "PDVSA", "Maraven",
           "Smith", "Baker",
           "Universidad del Zulia", "Miguel Enrique Lopez Gudiño", "Miguel Lopez"]
_PROTECT_RE = re.compile("(%s)" % "|".join(re.escape(n) for n in PROTECT))


def protect(h):
    """h is HTML. Wraps every protected name in translate="no"."""
    return _PROTECT_RE.sub(r'<span translate="no">\1</span>', h)


def T(tag, en, es, cls=None, rich=False, key=None, extra=""):
    """An element with English text and a Spanish version. rich=True lets the text hold HTML."""
    k = _key(key)
    body_en = en if rich else esc(en)
    body_es = es if rich else esc(es)
    p_en, p_es = protect(body_en), protect(body_es)
    use_html = rich or p_en != body_en or p_es != body_es
    ES[k] = p_es if use_html else es
    c = ' class="%s"' % cls if cls else ""
    attr = "data-i18n-html" if use_html else "data-i18n"
    body = p_en if use_html else body_en
    x = (" " + extra) if extra else ""
    return '<%s%s %s="%s"%s>%s</%s>' % (tag, c, attr, k, x, body, tag)


def A(name, en, es, key=None):
    """An attribute (aria-label, content) with a Spanish version."""
    k = _key(key)
    ES[k] = es
    return '%s="%s" data-i18n-attr="%s:%s"' % (name, escq(en), name, k)


# ---------------------------------------------------------------------------
# Shared pieces
# ---------------------------------------------------------------------------

NAV = [
    ("services.html", "Services", "Servicios", "services"),
    ("experience.html", "Experience", "Experiencia", "experience"),
    ("about.html", "About", "Sobre mí", "about"),
]


def header(current, root=""):
    items = []
    for href, en, es, name in NAV:
        cur = ' aria-current="page"' if current == name else ""
        items.append('          <li><a href="%s%s"%s %s="nav.%s">%s</a></li>' % (root, href, cur, "data-i18n", name, esc(en)))
        ES["nav." + name] = es
    cta_cur = ' aria-current="page"' if current == "contact" else ""
    ES["nav.contact"] = "Contacto"
    ES["nav.label"] = "Principal"
    ES["skip"] = "Saltar al contenido"
    return """  <a class="skip-link" href="#main" data-i18n="skip">Skip to content</a>

  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="%(root)sindex.html">
        <img src="%(root)sfavicon.svg" alt="" width="22" height="22">
        <span translate="no">%(name)s</span>
      </a>
      <nav class="site-nav" aria-label="Main" data-i18n-attr="aria-label:nav.label">
        <ul class="nav-list">
%(items)s
          <li><a class="nav-cta" href="%(root)scontact.html"%(cta_cur)s data-i18n="nav.contact">Contact</a></li>
          <li><button class="lang-btn" id="lang-toggle" type="button" lang="es">Español</button></li>
        </ul>
      </nav>
    </div>
  </header>
""" % {"root": root, "name": NAME, "items": "\n".join(items), "cta_cur": cta_cur}


def footer(root=""):
    ES["foot.top"] = "Volver arriba"
    ES["foot.contact"] = "Contacto"
    return """  <footer class="site-footer">
    <div class="wrap">
      <p>&copy; <span data-year>%(year)s</span> <span translate="no">%(name)s</span></p>
      <ul class="footer-links">
        <li><a href="%(root)scontact.html" data-i18n="foot.contact">Contact</a></li>
      </ul>
      <a href="#top" data-i18n="foot.top">Back to top</a>
    </div>
  </footer>
""" % {"year": YEAR, "name": NAME, "root": root}


def closing(root="", title=None, sub=None):
    """The big question and button at the bottom of a page. title and sub are (English, Spanish) pairs."""
    t = title or ("Have a well, a tender or a contract to talk about?",
                  "¿Tiene un pozo, una licitación o un contrato del que hablar?")
    key = (PAGE + ".closing.title") if title else "closing.title"
    sub_html = ""
    if sub:
        sub_html = "\n      " + T("p", sub[0], sub[1], cls="closing-sub", key=PAGE + ".closing.sub")
    return """    <section class="closing" aria-labelledby="closing-title">
      %s%s
      <p class="closing-action">%s</p>
    </section>""" % (
        T("h2", t[0], t[1], cls="closing-title", extra='id="closing-title"', key=key),
        sub_html,
        '<a class="btn" href="%scontact.html" data-i18n="closing.btn">Send me a message</a>' % root,
    )


ES["closing.btn"] = "Envíeme un mensaje"


def shell(page, current, title, desc, main, root="", indexable=False, body_attrs=""):
    """A complete page. title and desc are (English, Spanish) pairs."""
    robots = "" if indexable else '  <meta name="robots" content="noindex, nofollow">\n'
    ES[page + ".title"] = title[1]
    ES[page + ".desc"] = desc[1]
    ES[page + ".ogtitle"] = title[1]
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
%(robots)s  <title data-i18n="%(page)s.title">%(title)s</title>
  <meta name="description" content="%(desc)s" data-i18n-attr="content:%(page)s.desc">
  <meta name="theme-color" content="#d9dadd">
  <meta property="og:type" content="website">
  <meta property="og:title" content="%(title_q)s" data-i18n-attr="content:%(page)s.ogtitle">
  <meta property="og:description" content="%(desc)s" data-i18n-attr="content:%(page)s.desc">
  <link rel="icon" href="%(root)sfavicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
  <link rel="stylesheet" href="%(root)scss/styles.css?v=%(v)s">
</head>
<body id="top" data-page="%(current)s"%(battrs)s>
%(header)s
  <main id="main" class="%(mainclass)s">
%(main)s
  </main>

%(footer)s
  <script src="%(root)sjs/i18n.js?v=%(v)s"></script>
  <script src="%(root)sjs/site.js?v=%(v)s"></script>
</body>
</html>
""" % {
        "robots": robots, "page": page, "title": esc(title[0]), "title_q": escq(title[0]),
        "desc": escq(desc[0]), "root": root, "v": VERSION, "current": current,
        "header": header(current, root), "footer": footer(root), "main": main,
        "battrs": body_attrs,
        "mainclass": "lost wrap" if page == "notfound" else "page wrap",
    }


# ---------------------------------------------------------------------------
# The career, written once and used by the timeline strip and the Experience page
# ---------------------------------------------------------------------------

# (strip label or "", strip width in years, colour 1 or 2, company, years (from, to), roles)
CAREER = [
    {
        "id": "roku", "short": "", "w": 2, "c": 1, "company": "Roku Tech",
        "from": "2024", "to": None, "place": ("Bogotá, Colombia", "Bogotá, Colombia"),
        "roles": [(("Consulting and Sales Manager, Latin America", "Gerente de Consultoría y Ventas, Latinoamérica"), None)],
        "text": [
            ("Consulting for oil and gas companies, mainly on drilling and on fishing and remedial operations.",
             "Consultoría para empresas de petróleo y gas, principalmente en perforación y en operaciones de pesca y remediales."),
            ("The company also supports oil and gas extraction, rents machinery and equipment, and offers engineering and technical consulting.",
             "La empresa también apoya la extracción de petróleo y gas, alquila maquinaria y equipos, y ofrece ingeniería y consultoría técnica."),
        ],
    },
    {
        "id": "wis", "short": "", "w": 1, "c": 2, "company": "Wellbore Integrity Solutions",
        "from": "2023", "to": "2024", "place": None,
        "roles": [(("Country Operational Manager, Mexico and Central America", "Gerente Operativo de País, México y Centroamérica"), None)],
        "text": [
            ("I managed clients and results in Mexico, with responsibility for the profit and loss account and a team of 105 people. I led the tenders and the operating strategy.",
             "Dirigí los clientes y los resultados en México, con responsabilidad sobre el estado de pérdidas y ganancias y un equipo de 105 personas. Lideré las licitaciones y la estrategia operativa."),
            ("Revenue grew 70% year over year between 2022 and 2023, and profitability grew 115%. Days sales outstanding (DSO) fell by 60 days.",
             "Entre 2022 y 2023, los ingresos crecieron 70% frente al año anterior y la rentabilidad creció 115%. Los días de ventas por cobrar (DSO) se redujeron en 60 días."),
        ],
    },
    {
        "id": "nabors", "short": "Nabors", "w": 4, "c": 1, "company": "Nabors Drilling International",
        "from": "2018", "to": "2022", "place": None,
        "roles": [
            (("Contract and Marketing Manager, Colombia", "Gerente de Contratos y Mercadeo, Colombia"), ("2019", "2022")),
            (("Operations Manager, Ecuador", "Gerente de Operaciones, Ecuador"), ("2018", "2019")),
        ],
        "text": [
            ("In Colombia I managed client contracts and rig market opportunities, to raise the number of active rigs and widen the client base. I led the growth of Nabors Drilling Solutions, mainly casing and tubular running.",
             "En Colombia gestioné los contratos con clientes y las oportunidades del mercado de taladros, para aumentar los taladros activos y ampliar la base de clientes. Lideré el crecimiento de Nabors Drilling Solutions, sobre todo en corrida de revestimiento y tubulares."),
            ("I worked with automated rigs, performance automation, wellbore services and remote operations. I also worked on energy transition: hybrid energy systems and green fuels that reduce emissions.",
             "Trabajé con taladros automatizados, automatización del desempeño, servicios de pozo y operaciones remotas. También trabajé en la transición energética: sistemas de energía híbridos y combustibles verdes que reducen emisiones."),
            ("In Ecuador I led the restart of operations in the rig market. We began with a single rig, and it delivered outstanding performance.",
             "En Ecuador lideré la reactivación de las operaciones en el mercado de taladros. Comenzamos con un solo taladro, que tuvo un desempeño sobresaliente."),
        ],
    },
    {
        "id": "own", "short": "", "w": 1, "c": 2, "company": None,
        "company_t": ("Independent work", "Trabajo independiente"),
        "from": "2017", "to": "2018", "place": None,
        "roles": [(("Entrepreneur and consulting work", "Emprendimiento y trabajos de consultoría"), None)],
        "text": [],
    },
    {
        "id": "slb", "short": "Schlumberger", "w": 6, "c": 1, "company": "Schlumberger",
        "from": "2010", "to": "2016", "place": None,
        "roles": [
            (("Drill Bits and Drilling Tools Operation Manager, Brazil", "Gerente de Operaciones de Brocas y Herramientas de Perforación, Brasil"), ("2015", "2016")),
            (("Sales and Marketing Manager, Drilling Tools and Remedial, South America", "Gerente de Ventas y Mercadeo, Herramientas de Perforación y Remediales, Sudamérica"), ("2013", "2015")),
            (("Manager, Drilling Tools and Remedial, Peru, Colombia and Ecuador", "Gerente de Herramientas de Perforación y Remediales, Perú, Colombia y Ecuador"), ("2010", "2013")),
        ],
        "text": [
            ("In Brazil I led client relations and performance for bits and drilling tools. I was responsible for the profit and loss account and a team of 172 people, and I took part in tenders with several clients.",
             "En Brasil dirigí la relación con los clientes y el desempeño de barrenas y herramientas de perforación. Fui responsable del estado de pérdidas y ganancias y de un equipo de 172 personas, y participé en licitaciones con varios clientes."),
            ("For South America I set the marketing and sales strategy of the segment. That meant new technology, tender strategy, market analysis, competitor monitoring and input to research and development.",
             "Para Sudamérica definí la estrategia de mercadeo y ventas del segmento. Eso incluyó nuevas tecnologías, estrategia de licitaciones, análisis de mercado, seguimiento de la competencia y aportes a investigación y desarrollo."),
            ("Before that I led client relations and results for drilling tools and remedial services in Peru, Colombia and Ecuador.",
             "Antes dirigí la relación con los clientes y los resultados de herramientas de perforación y servicios remediales en Perú, Colombia y Ecuador."),
        ],
    },
    {
        "id": "smith", "short": "Smith", "w": 5, "c": 2, "company": "Smith International",
        "from": "2005", "to": "2010", "place": None,
        "roles": [
            (("Region Operation Manager, Remedial and Drilling Tools: Venezuela, Colombia, Ecuador and Peru", "Gerente de Operaciones Regional, Herramientas Remediales y de Perforación: Venezuela, Colombia, Ecuador y Perú"), ("2007", "2010")),
            (("Venezuela Country Operation Manager, Drilling and Remedial Tools", "Gerente de Operaciones de País en Venezuela, Herramientas de Perforación y Remediales"), ("2005", "2007")),
        ],
        "text": [
            ("I led a tenfold growth of the business by introducing new products, services and technologies in a competitive market where price mattered. I oversaw the facilities and civil works for the Neiva base, and I took part in the merger with Schlumberger.",
             "Lideré un crecimiento de diez veces del negocio al introducir nuevos productos, servicios y tecnologías en un mercado competitivo y sensible al precio. Supervisé las instalaciones y obras civiles de la base de Neiva, y participé en el proceso de fusión con Schlumberger."),
            ("Earlier, as country manager for Venezuela, I grew the business with the company's wider product range and won several contracts through tenders. I also expanded the base in Maturín.",
             "Antes, como gerente de país en Venezuela, hice crecer el negocio con el portafolio ampliado de la empresa y gané varios contratos mediante licitaciones. También amplié la base en Maturín."),
        ],
    },
    {
        "id": "bh", "short": "Baker Hughes", "w": 7, "c": 1, "company": "Baker Hughes",
        "from": "1997", "to": "2004", "place": None,
        "roles": [
            (("Latin America Drilling Optimization Manager, Integrated Projects", "Gerente de Optimización de Perforación para Latinoamérica, Proyectos Integrados"), ("2003", "2004")),
            (("Latin America OASIS Senior Drilling Optimization Engineer", "Ingeniero Senior de Optimización de Perforación OASIS, Latinoamérica"), ("2001", "2003")),
            (("Venezuela Drilling Operation Manager", "Gerente de Operaciones de Perforación, Venezuela"), ("1999", "2001")),
            (("Venezuela Drilling Integration and Operations Manager", "Gerente de Integración y Operaciones de Perforación, Venezuela"), ("1998", "1999")),
            (("Venezuela Drilling Integration Coordinator", "Coordinador de Integración de Perforación, Venezuela"), ("1997", "1998")),
        ],
        "text": [
            ("I managed integrated projects that used new technology for directional wells, such as rotary steerable and vertical drilling systems. In western Venezuela they cut drilling time and reached the geological targets.",
             "Gestioné proyectos integrados con nuevas tecnologías para pozos direccionales, como sistemas rotativos direccionales y de perforación vertical. En el occidente de Venezuela redujeron el tiempo de perforación y alcanzaron los objetivos geológicos."),
            ("On the OASIS team I analyzed drilling performance in Venezuela, Colombia, Argentina, Bolivia, Brazil, Ecuador, Peru and Trinidad and Tobago. The aim was to cut time and cost for clients without raising the well budget (AFE).",
             "En el equipo OASIS analicé el desempeño de la perforación en Venezuela, Colombia, Argentina, Bolivia, Brasil, Ecuador, Perú y Trinidad y Tobago. El objetivo era reducir tiempo y costos para los clientes sin aumentar el presupuesto del pozo (AFE)."),
            ("On the Morichal project I managed field and administrative operations for 20 re-entry wells. They reached their geological targets and were drilled in record time.",
             "En el proyecto Morichal gestioné las operaciones de campo y administrativas de 20 pozos de reentrada. Alcanzaron sus objetivos geológicos y se perforaron en tiempo récord."),
        ],
    },
    {
        "id": "pdvsa", "short": "PDVSA", "w": 10, "c": 2, "company": "PDVSA",
        "from": "1987", "to": "1997", "place": None,
        "roles": [
            (("Budget Analyst, Maraven", "Analista de Presupuesto, Maraven"), ("1994", "1997")),
            (("Drilling and Workover Coordinator, West Venezuela", "Coordinador de Perforación y Reacondicionamiento, Occidente de Venezuela"), ("1988", "1994")),
            (("Reservoir Engineer, West Venezuela", "Ingeniero de Yacimientos, Occidente de Venezuela"), ("1987", "1988")),
        ],
        "text": [
            ("I started as a reservoir engineer on Lake Maracaibo, then moved to offshore drilling and workover. I led a team of five engineers and four workover rigs.",
             "Comencé como ingeniero de yacimientos en el Lago de Maracaibo y pasé luego a perforación y reacondicionamiento costa afuera. Dirigí un equipo de cinco ingenieros y cuatro taladros de reacondicionamiento."),
            ("My last role was budget analyst: I calculated the yearly investment budgets (AFEs) for all the drilling work of the Petroleum Engineering Department.",
             "Mi último cargo fue analista de presupuesto: calculé los presupuestos anuales de inversión (AFE) de todas las actividades de perforación del Departamento de Ingeniería de Petróleo."),
        ],
    },
]


def years_t(a, b):
    """English and Spanish text for a span of years."""
    if b is None:
        return ("%s to now" % a, "%s a hoy" % a)
    if a == b:
        return (a, a)
    return ("%s to %s" % (a, b), "%s a %s" % (a, b))


def strip(prefix):
    """The career strip: one block per company, wide as the years spent there, oldest on the left."""
    label_en = ("Career timeline from 1987 to today: PDVSA, Baker Hughes, Smith International, "
                "Schlumberger, independent work, Nabors, Wellbore Integrity Solutions and Roku Tech.")
    label_es = ("Línea de tiempo de la carrera de 1987 a hoy: PDVSA, Baker Hughes, Smith International, "
                "Schlumberger, trabajo independiente, Nabors, Wellbore Integrity Solutions y Roku Tech.")
    blocks = []
    for e in reversed(CAREER):
        label = ('<b translate="no">%s</b>' % esc(e["short"])) if e["short"] else ""
        blocks.append('<span class="c%d" style="--w: %d">%s</span>' % (e["c"], e["w"], label))
    ES["strip.now"] = "Hoy"
    return """<figure class="strip-wrap">
      <div class="strip" role="img" %s>
        %s
      </div>
      <p class="strip-axis" aria-hidden="true"><span>1987</span><span data-i18n="strip.now">Today</span></p>
    </figure>""" % (A("aria-label", label_en, label_es, key=prefix + ".strip.label"), "\n        ".join(blocks))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def page_home():
    global PAGE
    PAGE = "home"

    def tiles(items, cls=""):
        out = []
        for ic, en, es in items:
            out.append('          <li class="tile" style="--t: %s">%s%s</li>' % (ICONS[ic][1], icon(ic), T("span", en, es)))
        return '<ul class="tiles%s">\n%s\n        </ul>' % (cls, "\n".join(out))

    def row(rid, title, text, body, href, btn, art, art_cls=""):
        return """      <section class="row row--art" aria-labelledby="%s">
        <div class="row-main">
          %s
          %s
          %s
          <p class="row-foot"><a class="btn" href="%s" data-i18n="%s">%s</a></p>
        </div>
        <div class="row-art%s">%s</div>
      </section>""" % (rid,
                       T("h2", title[0], title[1], cls="row-title", extra='id="%s"' % rid),
                       T("p", text[0], text[1], cls="row-text"),
                       body, href, _reg(btn[1]), esc(btn[0]), art_cls, art)

    services = [("derrick", "Drilling and remedial", "Perforación y remediales"),
                ("gauge", "Drilling optimization", "Optimización"),
                ("contract", "Tenders and contracts", "Licitaciones y contratos"),
                ("magnifier", "Assessments", "Evaluaciones"),
                ("trend", "Profitability", "Rentabilidad"),
                ("sprout", "Teams and talent", "Equipos y talento")]
    about = [("cap", "Universidad del Zulia", "Universidad del Zulia"),
             ("speech", "Three languages", "Tres idiomas"),
             ("clock", "Since 1987", "Desde 1987"),
             ("pin", "Bogotá, Colombia", "Bogotá, Colombia")]
    rows = [
        row("row-services", ("How I can help", "Cómo puedo ayudar"),
            ("Drilling optimization, remedial operations, tenders and contracts, and team development.",
             "Optimización de perforación, operaciones remediales, licitaciones y contratos, y desarrollo de equipos."),
            tiles(services, " tiles--3"), "services.html", ("See the services", "Ver los servicios"),
            pic("assets/scenes/midday-card.svg", None, 800, 600)),
        row("row-experience", ("More than 37 years", "Más de 37 años"),
            ("From reservoir engineer at PDVSA to country and regional manager at Baker Hughes, Smith International, Schlumberger and Nabors.",
             "De ingeniero de yacimientos en PDVSA a gerente de país y regional en Baker Hughes, Smith International, Schlumberger y Nabors."),
            strip("home"), "experience.html", ("See the career log", "Ver la trayectoria"),
            pic("assets/about/americas-map.svg", None, 760, 860), " row-art--map"),
        row("row-about", ("About me", "Sobre mí"),
            ("My degree in petroleum engineering, how I came to the industry and how I run teams and projects.",
             "Mi título de ingeniero de petróleo, cómo llegué a la industria y cómo dirijo equipos y proyectos."),
            tiles(about), "about.html", ("Read more about me", "Conocer más sobre mí"),
            pic("assets/scenes/dusk-card.svg", None, 800, 600)),
    ]
    main = """    <section class="hero">
      %s
      %s
      %s
    </section>

    %s

    <div class="rows">
%s
    </div>

%s""" % (
        T("h1", "Drilling and well intervention", "Perforación e intervención de pozos", cls="hero-title"),
        T("p", "I am a senior petroleum engineer with more than 37 years in oil and gas across Latin America. I consult on drilling, fishing and remedial operations, on tenders and contracts, and on operational performance.",
          "Soy ingeniero de petróleo senior, con más de 37 años en petróleo y gas en toda Latinoamérica. Asesoro en perforación, en operaciones de pesca y remediales, en licitaciones y contratos, y en desempeño operacional.",
          cls="lede"),
        T("p", "Based in Bogotá, Colombia. Consulting for oil and gas companies across Latin America.",
          "Con sede en Bogotá, Colombia. Consultoría para empresas de petróleo y gas en toda Latinoamérica.",
          cls="hero-note"),
        cover("gold"), "\n\n".join(rows), closing())
    return shell("home", "home",
                 ("Miguel Lopez | Drilling and well intervention consultant", "Miguel Lopez | Consultor en perforación e intervención de pozos"),
                 ("Miguel Lopez is a senior petroleum engineer with more than 37 years in oil and gas across Latin America. Consulting on drilling, remedial operations, tenders and contracts.",
                  "Miguel Lopez es ingeniero de petróleo senior con más de 37 años en petróleo y gas en Latinoamérica. Consultoría en perforación, operaciones remediales, licitaciones y contratos."),
                 main)


def _reg(es, key=None):
    """Registers a Spanish text for an element written by hand and returns its key."""
    k = _key(key)
    ES[k] = es
    return k


def _attr_key(name, key, en, es):
    ES[key] = es
    return '%s="%s" data-i18n-attr="%s:%s"' % (name, escq(en), name, key)


def pic(src, alt=None, w=0, h=0, cls=None, root=""):
    """An image. alt=None draws a decorative one (empty alt); alt=(English, Spanish) describes it."""
    c = ' class="%s"' % cls if cls else ""
    a = 'alt=""' if alt is None else A("alt", alt[0], alt[1])
    return '<img%s src="%s%s" %s width="%d" height="%d">' % (c, root, src, a, w, h)


def icon(name, size=40, root=""):
    return pic("assets/icons/%s.svg" % name, None, size, size, root=root)


def cover(name, root=""):
    """The wide picture at the top of a page. It fades out at both sides."""
    return '<div class="cover">%s</div>' % pic("assets/scenes/%s.svg" % name, None, 2500, 667, root=root)


def map_figure():
    caption = T("figcaption",
                "Where I have worked: Venezuela, Colombia, Ecuador, Peru, Brazil, Argentina, Bolivia, Trinidad and Tobago, Mexico and Central America.",
                "Dónde he trabajado: Venezuela, Colombia, Ecuador, Perú, Brasil, Argentina, Bolivia, Trinidad y Tobago, México y Centroamérica.")
    img = pic("assets/about/americas-map.svg",
              ("Map of the Americas with a pin on each country where Miguel has worked",
               "Mapa de América con un marcador en cada país donde Miguel ha trabajado"), 760, 860)
    return '<figure class="map">%s%s</figure>' % (img, caption)


SERVICES = [
    ("Drilling, fishing and remedial operations", "Perforación, pesca y operaciones remediales",
     "Consulting for oil and gas companies on drilling, fishing and remedial work, including the activities that support extraction.",
     "Consultoría para empresas de petróleo y gas en perforación, pesca y trabajos remediales, incluidas las actividades que apoyan la extracción."),
    ("Drilling optimization", "Optimización de la perforación",
     "Analysis of drilling performance to reduce time and cost. New technology is brought in without raising the well budget (AFE).",
     "Análisis del desempeño de la perforación para reducir tiempo y costos. Se incorporan nuevas tecnologías sin aumentar el presupuesto del pozo (AFE)."),
    ("Tenders and contracts", "Licitaciones y contratos",
     "Preparing and negotiating tenders and contracts in several countries, so that products and services arrive on time and at the quality the client expects.",
     "Preparación y negociación de licitaciones y contratos en varios países, para que los productos y servicios lleguen a tiempo y con la calidad que el cliente espera."),
    ("Business and technology assessments", "Evaluaciones de negocio y tecnología",
     "Reviews of a business line or a technology: how assets are used, where downtime comes from, and how pricing and market position can improve.",
     "Revisión de una línea de negocio o de una tecnología: cómo se usan los activos, de dónde viene el tiempo no productivo y cómo mejorar los precios y la posición en el mercado."),
    ("Operations and profitability", "Operaciones y rentabilidad",
     "Turning operations around through pricing, client growth, cost control and collections. At Wellbore Integrity Solutions in Mexico, revenue grew 70% year over year and profitability 115%.",
     "Recuperación de operaciones mediante precios, crecimiento de clientes, control de costos y cobranza. En Wellbore Integrity Solutions en México, los ingresos crecieron 70% frente al año anterior y la rentabilidad 115%."),
    ("Teams and local talent", "Equipos y talento local",
     "Training, succession planning and capability building, so that field teams and local technical staff can take the lead.",
     "Formación, planes de sucesión y desarrollo de capacidades, para que los equipos de campo y el personal técnico local puedan asumir el liderazgo."),
]


SERVICE_ICONS = ["derrick", "gauge", "contract", "magnifier", "trend", "sprout"]
SERVICE_CARDS = ["svc-drilling", "svc-optimize", "svc-tender", "svc-assess", "svc-profit", "svc-team"]


def page_services():
    global PAGE
    PAGE = "services"
    rows = []
    for (t_en, t_es, p_en, p_es), ic, card in zip(SERVICES, SERVICE_ICONS, SERVICE_CARDS):
        rows.append("""      <li class="service">
        <div class="service-art">%s</div>
        <div class="service-body">
          <div class="service-head">
            <span class="icon-box icon-box--big" style="--t: %s">%s</span>
            %s
          </div>
          %s
        </div>
      </li>""" % (pic("assets/cards/%s.svg" % card, None, 800, 600), ICONS[ic][1], icon(ic, 40),
                  T("h2", t_en, t_es, cls="service-title"), T("p", p_en, p_es, cls="service-text")))
    steps = [("Evaluate progress", "Evaluar el avance"), ("Optimize strategies", "Optimizar las estrategias"),
             ("Make decisions", "Tomar decisiones"), ("Measure performance", "Medir el desempeño")]
    tints = ["#ffe9dc", "#def2ef", "#e0e7fe", "#f9e2ea"]
    method = "\n".join('        <li class="tile" style="--t: %s"><b class="step-no" aria-hidden="true">%d</b>%s</li>' % (tints[i], i + 1, T("span", a, b))
                       for i, (a, b) in enumerate(steps))
    main = """    <h1 class="hero-title">%s</h1>
    %s

    %s

    <ul class="services">
%s
    </ul>

    <section class="row method" aria-labelledby="method-title">
      %s
      %s
      <ol class="tiles tiles--steps">
%s
      </ol>
    </section>

%s""" % (
        T("span", "How I can help", "Cómo puedo ayudar", key="services.h1"),
        T("p", "I work with oil and gas operators and service companies. These are the areas where I can add the most.",
          "Trabajo con operadoras y empresas de servicios de petróleo y gas. Estas son las áreas donde más puedo aportar.", cls="lede"),
        cover("midday"), "\n".join(rows),
        T("h2", "How I work", "Cómo trabajo", cls="row-title", extra='id="method-title"'),
        T("p", "I work from data and numbers. My method has four steps.",
          "Trabajo con datos y cifras. Mi método tiene cuatro pasos.", cls="row-text"),
        method, closing())
    return shell("services", "services",
                 ("Services | Miguel Lopez", "Servicios | Miguel Lopez"),
                 ("Drilling and remedial consulting, drilling optimization, tenders and contracts, business assessments and team development for oil and gas companies.",
                  "Consultoría en perforación y operaciones remediales, optimización de perforación, licitaciones y contratos, evaluaciones de negocio y desarrollo de equipos para empresas de petróleo y gas."),
                 main)


LOG_ICONS = {"roku": "magnifier", "wis": "trend", "nabors": "cycle", "own": "sprout",
             "slb": "contract", "smith": "people", "bh": "gauge", "pdvsa": "derrick"}


def page_experience():
    global PAGE
    PAGE = "experience"
    items = []
    for e in CAREER:
        yrs = years_t(e["from"], e["to"])
        name = ('<span translate="no">%s</span>' % esc(e["company"])) if e["company"] else T("span", e["company_t"][0], e["company_t"][1])
        place = ""
        if e["place"]:
            place = '<p class="log-place">%s</p>' % esc(e["place"][0])
        roles = []
        for (r_en, r_es), span in e["roles"]:
            sp = ""
            if span:
                s_en, s_es = years_t(*span)
                sp = ' <span class="log-role-years">%s</span>' % T("span", s_en, s_es)
            roles.append("          <li>%s%s</li>" % (T("span", r_en, r_es, cls="log-role"), sp))
        paras = "\n".join("        " + T("p", a, b) for a, b in e["text"])
        items.append("""      <li class="log-item c%(c)d" id="%(id)s">
        <p class="log-years">%(yrs)s</p>
        <div class="log-rail" aria-hidden="true"></div>
        <div class="log-body">
          <div class="log-head">
            <span class="icon-box" style="--t: %(tint)s">%(icon)s</span>
            <h2 class="log-company">%(name)s</h2>
          </div>
          <div class="log-art">%(art)s</div>
          <div class="log-main">
%(place)s
          <ul class="log-roles">
%(roles)s
          </ul>
%(paras)s
          </div>
        </div>
      </li>""" % {"c": e["c"], "id": e["id"], "yrs": T("span", yrs[0], yrs[1]), "name": name,
                   "tint": ICONS[LOG_ICONS[e["id"]]][1], "icon": icon(LOG_ICONS[e["id"]], 32),
                   "place": place, "roles": "\n".join(roles), "paras": paras,
                   "art": pic("assets/cards/job-%s.svg" % e["id"], None, 800, 600)})
    main = """    <div class="exp-top">
      <div class="exp-text">
        <h1 class="hero-title">%s</h1>
        %s
        %s
      </div>
      %s
    </div>

    <ol class="log">
%s
    </ol>

%s""" % (
        T("span", "Career log", "Trayectoria", key="experience.h1"),
        T("p", "More than 37 years in oil and gas, newest first. Each block on the strip is as wide as the years spent there.",
          "Más de 37 años en petróleo y gas, de lo más reciente a lo más antiguo. Cada bloque de la franja es tan ancho como los años dedicados.", cls="lede"),
        strip("experience"), map_figure(), "\n".join(items), closing())
    return shell("experience", "experience",
                 ("Experience | Miguel Lopez", "Experiencia | Miguel Lopez"),
                 ("Career log of Miguel Lopez: PDVSA, Baker Hughes, Smith International, Schlumberger, Nabors, Wellbore Integrity Solutions and Roku Tech.",
                  "Trayectoria de Miguel Lopez: PDVSA, Baker Hughes, Smith International, Schlumberger, Nabors, Wellbore Integrity Solutions y Roku Tech."),
                 main)


def page_about():
    global PAGE
    PAGE = "about"
    strengths = [
        ("shield", ("Execution and risk management", "Ejecución y gestión de riesgos"),
         ("Well intervention procedures, early risk control and decisive leadership under pressure.",
          "Procedimientos de intervención de pozos, control anticipado de riesgos y liderazgo firme bajo presión.")),
        ("badge", ("Service quality", "Calidad del servicio"),
         ("Every phase of the work follows the service level agreements (SLAs) and what the client expects.",
          "Cada fase del trabajo sigue los acuerdos de nivel de servicio (SLA) y lo que el cliente espera.")),
        ("cycle", ("Efficiency and profit", "Eficiencia y rentabilidad"),
         ("Continuous improvement, better workflows and cost control to raise project margins.",
          "Mejora continua, mejores flujos de trabajo y control de costos para aumentar los márgenes de los proyectos.")),
        ("people", ("Leadership and local talent", "Liderazgo y talento local"),
         ("Leading field teams from several disciplines, training local people and planning succession so operations keep running.",
          "Dirección de equipos de campo de varias disciplinas, formación de personal local y planes de sucesión para que la operación no se detenga.")),
    ]
    lis = []
    for ic, (t_en, t_es), (p_en, p_es) in strengths:
        lis.append("""          <li class="strength">
            <span class="icon-box" style="--t: %s">%s</span>
            <div>
              %s
              %s
            </div>
          </li>""" % (ICONS[ic][1], icon(ic, 32), T("h3", t_en, t_es, cls="strength-title"), T("p", p_en, p_es)))
    facts = [
        ("cap", ("Education", "Estudios"),
         ("Petroleum Engineering, Universidad del Zulia, 1989", "Ingeniería de Petróleo, Universidad del Zulia, 1989")),
        ("speech", ("Languages", "Idiomas"),
         ("English and Spanish, fluent. Portuguese, intermediate.", "Inglés y español, con fluidez. Portugués, nivel intermedio.")),
        ("clock", ("Experience", "Experiencia"), ("Since 1987", "Desde 1987")),
        ("pin", ("Based in", "Con sede en"), ("Bogotá, Colombia", "Bogotá, Colombia")),
    ]
    fs = []
    for ic, (l_en, l_es), (v_en, v_es) in facts:
        fs.append("""          <div class="fact" style="--t: %s">
            <dt>%s%s</dt>
            <dd>%s</dd>
          </div>""" % (ICONS[ic][1], icon(ic, 36), T("span", l_en, l_es), T("span", v_en, v_es)))
    main = """    <article class="profile" aria-labelledby="profile-name">
      <div class="cover profile-cover">%(cover)s</div>

      <div class="profile-head">
        %(badge)s
        <h1 class="profile-name" id="profile-name" translate="no">Miguel Enrique Lopez Gudiño</h1>
        %(place)s
        %(lede)s
      </div>

      <div class="profile-body">
        <section class="profile-section profile-story" aria-labelledby="start-title">
          %(h_start)s
          %(p1)s
          %(p2)s
          %(p3)s

          %(h_track)s
          %(p4)s
          %(p5)s
          <ul class="strengths">
%(lis)s
          </ul>
        </section>

        <div class="profile-side">
          <section class="profile-section" aria-labelledby="glance-title">
            %(h_glance)s
            <dl class="glance">
%(fs)s
            </dl>
          </section>

          <section class="profile-section" aria-labelledby="map-title">
            %(h_map)s
            %(map)s
          </section>
        </div>
      </div>
    </article>

%(closing)s""" % {
        "cover": pic("assets/scenes/dusk.svg", None, 2500, 667),
        "badge": pic("assets/about/profile-badge.svg",
                     ("Illustration of a drilling derrick, in place of a portrait", "Ilustración de una torre de perforación, en lugar de un retrato"),
                     640, 640, cls="profile-photo"),
        "place": T("p", "Senior petroleum engineer, Bogotá, Colombia", "Ingeniero de petróleo senior, Bogotá, Colombia", cls="profile-place"),
        "lede": T("p", "More than 37 years turning complex operating problems into results that are measurable, safe and profitable for oil and gas companies.",
                  "Más de 37 años convirtiendo problemas operativos complejos en resultados medibles, seguros y rentables para empresas de petróleo y gas.",
                  cls="profile-lede"),
        "h_start": T("h2", "Where it started", "Cómo empezó", extra='id="start-title"'),
        "p1": T("p", "My link with the oil industry began long before I stood on a rig. I grew up in Northwestern Venezuela, moving from town to town and city to city because my parents' jobs kept relocating the family.",
                "Mi vínculo con la industria petrolera comenzó mucho antes de pisar un taladro. Crecí en el noroccidente de Venezuela, mudándome de pueblo en pueblo y de ciudad en ciudad porque los trabajos de mis padres los trasladaban con frecuencia."),
        "p2": T("p", "On our trips to Zulia State, the heart of Venezuelan oil, I watched pumpjacks nodding and flares burning day and night. That image stayed with me. I studied Petroleum Engineering at Universidad del Zulia (LUZ) and graduated in 1989.",
                "En nuestros viajes al estado Zulia, el corazón petrolero de Venezuela, veía los balancines subir y bajar y los mechurrios arder de día y de noche. Esa imagen me marcó. Estudié Ingeniería de Petróleo en la Universidad del Zulia (LUZ) y me gradué en 1989."),
        "p3": T("p", "Growing up on the move gave me adaptability, resilience and an easy way with people from very different backgrounds. It is the base of how I lead in the field: I fit into any operation, learn the local dynamics and build trust from the wellsite crew to senior management.",
                "Crecer en movimiento me dio adaptabilidad, resiliencia y facilidad para tratar con personas de todo tipo de orígenes. Es la base de mi liderazgo en campo: me integro a cualquier operación, entiendo la dinámica local y construyo confianza desde la cuadrilla en el pozo hasta la alta gerencia."),
        "h_track": T("h2", "Track record", "Trayectoria y resultados", cls="profile-h2--next"),
        "p4": T("p", "I have led operations and projects across Latin America with one standard: comply strictly with what was agreed, then beat the targets. There is little room for error in this industry, so I combine close technical control in the field with a focus on efficiency and profit.",
                "He dirigido operaciones y proyectos en toda Latinoamérica con un solo estándar: cumplir estrictamente lo acordado y luego superar las metas. En esta industria hay poco margen de error, por eso combino un control técnico cercano en campo con un enfoque en eficiencia y rentabilidad."),
        "p5": T("p", "As a technical consultant and advisor, I help operators and oilfield service companies with key decisions. My strengths:",
                "Como consultor y asesor técnico, ayudo a operadoras y empresas de servicios petroleros en decisiones clave. Mis fortalezas:"),
        "lis": "\n".join(lis),
        "h_glance": T("h2", "At a glance", "De un vistazo", extra='id="glance-title"'),
        "fs": "\n".join(fs),
        "h_map": T("h2", "Where I have worked", "Dónde he trabajado", extra='id="map-title"'),
        "map": map_figure(),
        "closing": closing(title=("Need to reduce field risk or meet your contract targets?",
                                  "¿Necesita reducir los riesgos en campo o cumplir las metas de su contrato?"),
                           sub=("Put more than 37 years of hands-on experience in Latin America to work on your next project.",
                                "Ponga más de 37 años de experiencia práctica en Latinoamérica a trabajar en su próximo proyecto.")),
    }
    return shell("about", "about",
                 ("About | Miguel Lopez", "Sobre mí | Miguel Lopez"),
                 ("About Miguel Lopez: how he came to oil and gas, his track record across Latin America, his languages and where he has worked.",
                  "Sobre Miguel Lopez: cómo llegó al petróleo y al gas, su trayectoria en Latinoamérica, sus idiomas y dónde ha trabajado."),
                 main)


def page_contact():
    global PAGE
    PAGE = "contact"
    ES["contact.name"] = "Su nombre"
    ES["contact.email"] = "Su correo electrónico"
    ES["contact.note"] = "Solo se usa para responderle."
    ES["contact.message"] = "Su mensaje"
    ES["contact.send"] = "Enviar mensaje"
    main = """    <h1 class="hero-title">%(h1)s</h1>

    <div class="contact-grid">
      <div class="contact-intro">
        %(lede)s
        <div class="contact-art">%(art)s</div>
      </div>

      <!--
        This form sends messages through Web3Forms, which forwards them to the inbox that the access
        key was created for. No email address is written on this page. The access key is public by
        design: it only lets people send messages to that inbox. To get a key, open web3forms.com,
        enter the inbox address, and paste the key into the access_key field below.
      -->
      <form class="form" id="contact-form" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="YOUR_ACCESS_KEY_HERE">
        <input type="hidden" name="subject" value="New message from your website">
        <input type="hidden" name="from_name" value="Website">
        <input type="checkbox" name="botcheck" style="display: none;" tabindex="-1" autocomplete="off">

        <div class="field">
          <label for="name" data-i18n="contact.name">Your name</label>
          <input id="name" name="name" type="text" autocomplete="name" required>
        </div>

        <div class="field">
          <label for="email" data-i18n="contact.email">Your email</label>
          <input id="email" name="email" type="email" autocomplete="email" required aria-describedby="email-note">
          <p class="field-note" id="email-note" data-i18n="contact.note">Only used to reply to you.</p>
        </div>

        <div class="field">
          <label for="message" data-i18n="contact.message">Your message</label>
          <textarea id="message" name="message" rows="6" required></textarea>
        </div>

        <button class="btn" type="submit" data-i18n="contact.send">Send message</button>
        <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>""" % {
        "h1": T("span", "Contact", "Contacto", key="contact.h1"),
        "art": pic("assets/scenes/dawn-card.svg", None, 800, 600),
        "lede": T("p", "Have a project in mind? Send me a message and I will reply by email.",
                  "¿Tiene un proyecto en mente? Envíeme un mensaje y le responderé por correo electrónico.", cls="lede"),
    }
    return shell("contact", "contact",
                 ("Contact | Miguel Lopez", "Contacto | Miguel Lopez"),
                 ("Send Miguel Lopez a message about a drilling, remedial, tender or contract project.",
                  "Envíe un mensaje a Miguel Lopez sobre un proyecto de perforación, operaciones remediales, licitaciones o contratos."),
                 main)


def page_404():
    global PAGE
    PAGE = "notfound"
    ES["notfound.btn1"] = "Ver los servicios"
    ES["notfound.btn2"] = "Ver la trayectoria"
    main = """    %s
    %s
    <p class="actions">
      <a class="btn" href="/services.html" data-i18n="notfound.btn1">See the services</a>
      <a class="btn btn--quiet" href="/experience.html" data-i18n="notfound.btn2">See the career log</a>
    </p>

    %s""" % (
        T("h1", "This page does not exist", "Esta página no existe", cls="hero-title"),
        T("p", "The link may be out of date or mistyped. Try one of these instead.",
          "Es posible que el enlace esté desactualizado o mal escrito. Pruebe con uno de estos.", cls="lede lede--after"),
        cover("dawn", root="/"))
    return shell("notfound", "404", ("Page not found | Miguel Lopez", "Página no encontrada | Miguel Lopez"),
                 ("This page does not exist.", "Esta página no existe."), main, root="/")


# ---------------------------------------------------------------------------

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    pages = {
        "index.html": page_home(),
        "services.html": page_services(),
        "experience.html": page_experience(),
        "about.html": page_about(),
        "contact.html": page_contact(),
        "404.html": page_404(),
    }
    for name, text in pages.items():
        write(name, text)
    # messages that site.js shows
    ES["js.sending"] = "Enviando..."
    ES["js.sent"] = "Gracias, su mensaje fue enviado. Le responderé por correo electrónico."
    ES["js.fail"] = "Su mensaje no se envió. Revise su conexión e inténtelo de nuevo."
    ES["js.off"] = "Este formulario aún no está activado."
    ES["lang.to"] = "English"
    ordered = {k: ES[k] for k in sorted(ES)}
    write("js/i18n.js", "/* Spanish text for the site. Written by tools/build.py, do not edit by hand. */\nwindow.I18N_ES = %s;\n"
          % json.dumps(ordered, ensure_ascii=False, indent=1))
    print("built %d pages, %d Spanish texts" % (len(pages), len(ES)))


if __name__ == "__main__":
    main()
