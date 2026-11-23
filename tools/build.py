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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "20261123a"      # change it whenever css/styles.css or a .js file changes
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


def T(tag, en, es, cls=None, rich=False, key=None, extra=""):
    """An element with English text and a Spanish version. rich=True lets the text hold HTML."""
    k = _key(key)
    ES[k] = es
    c = ' class="%s"' % cls if cls else ""
    attr = "data-i18n-html" if rich else "data-i18n"
    body = en if rich else esc(en)
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
        <span>%(name)s</span>
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
      <p>&copy; <span data-year>%(year)s</span> %(name)s</p>
      <ul class="footer-links">
        <li><a href="%(root)scontact.html" data-i18n="foot.contact">Contact</a></li>
      </ul>
      <a href="#top" data-i18n="foot.top">Back to top</a>
    </div>
  </footer>
""" % {"year": YEAR, "name": NAME, "root": root}


def closing(root=""):
    return """    <section class="closing" aria-labelledby="closing-title">
      %s
      <p class="closing-action">%s</p>
    </section>""" % (
        T("h2", "Have a well, a tender or a contract to talk about?",
          "¿Tiene un pozo, una licitación o un contrato del que hablar?",
          cls="closing-title", extra='id="closing-title"', key="closing.title"),
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
            ("Revenue grew 70% year over year between 2022 and 2023, and profitability grew 115%. Days sales outstanding fell by 60.",
             "Los ingresos crecieron 70% interanual entre 2022 y 2023, y la rentabilidad creció 115%. Los días de cobro pendientes bajaron 60."),
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
            (("Drill Bits and Drilling Tools Operation Manager, Brazil", "Gerente de Operaciones de Barrenas y Herramientas de Perforación, Brasil"), ("2015", "2016")),
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
            ("On the OASIS team I analysed drilling performance in Venezuela, Colombia, Argentina, Bolivia, Brazil, Ecuador, Peru and Trinidad and Tobago. The aim was to cut time and cost for clients without raising the well budget (AFE).",
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
        label = ('<b>%s</b>' % esc(e["short"])) if e["short"] else ""
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
    cards = [
        ("How I can help", "Cómo puedo ayudar",
         "Drilling optimization, remedial operations, tenders and contracts, and team development.",
         "Optimización de perforación, operaciones remediales, licitaciones y contratos, y desarrollo de equipos.",
         "services.html", "See the services", "Ver los servicios"),
        ("More than 37 years", "Más de 37 años",
         "From reservoir engineer at PDVSA to country and regional manager at Baker Hughes, Smith International, Schlumberger and Nabors.",
         "De ingeniero de yacimientos en PDVSA a gerente de país y regional en Baker Hughes, Smith International, Schlumberger y Nabors.",
         "experience.html", "See the career log", "Ver la trayectoria"),
        ("About me", "Sobre mí",
         "My degree in petroleum engineering, the languages I work in and how I run teams and projects.",
         "Mi título de ingeniero de petróleo, los idiomas en que trabajo y cómo dirijo equipos y proyectos.",
         "about.html", "Read more about me", "Conocer más sobre mí"),
    ]
    cs = []
    for t_en, t_es, p_en, p_es, href, b_en, b_es in cards:
        cs.append("""        <article class="card">
          %s
          %s
          <p class="card-foot"><a class="btn" href="%s" data-i18n="%s">%s</a></p>
        </article>""" % (T("h2", t_en, t_es, cls="card-title"), T("p", p_en, p_es), href, _reg(b_es), esc(b_en)))
    main = """    <section class="hero">
      %s
      %s
      %s
    </section>

    %s

    <section class="cards" %s>
%s
    </section>

%s""" % (
        T("h1", "Drilling and well intervention", "Perforación e intervención de pozos", cls="hero-title"),
        T("p", "I am a senior petroleum engineer with more than 37 years in oil and gas across Latin America. I consult on drilling, fishing and remedial operations, on tenders and contracts, and on operational performance.",
          "Soy ingeniero de petróleo senior, con más de 37 años en petróleo y gas en toda Latinoamérica. Asesoro en perforación, en operaciones de pesca y remediales, en licitaciones y contratos, y en desempeño operacional.",
          cls="lede"),
        T("p", "Based in Bogotá, Colombia. Consulting for oil and gas companies across Latin America.",
          "Con sede en Bogotá, Colombia. Consultoría para empresas de petróleo y gas en toda Latinoamérica.",
          cls="hero-note"),
        strip("home"),
        _attr_key("aria-label", "home.cards", "Where to start", "Por dónde empezar"),
        "\n".join(cs), closing())
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
     "Revisión de una línea de negocio o de una tecnología: cómo se usan los activos, de dónde viene el tiempo perdido y cómo mejorar los precios y la posición en el mercado."),
    ("Operations and profitability", "Operaciones y rentabilidad",
     "Turning operations around through pricing, client growth, cost control and collections. At Wellbore Integrity Solutions in Mexico, revenue grew 70% year over year and profitability 115%.",
     "Recuperación de operaciones mediante precios, crecimiento de clientes, control de costos y cobranza. En Wellbore Integrity Solutions en México, los ingresos crecieron 70% interanual y la rentabilidad 115%."),
    ("Teams and local talent", "Equipos y talento local",
     "Training, succession planning and capability building, so that field teams and local technical staff can take the lead.",
     "Formación, planes de sucesión y desarrollo de capacidades, para que los equipos de campo y el personal técnico local puedan asumir el liderazgo."),
]


def page_services():
    global PAGE
    PAGE = "services"
    rows = []
    for t_en, t_es, p_en, p_es in SERVICES:
        rows.append("""      <li class="service">
        %s
        %s
      </li>""" % (T("h2", t_en, t_es, cls="service-title"), T("p", p_en, p_es, cls="service-text")))
    main = """    <h1 class="hero-title">%s</h1>
    %s

    <ul class="services">
%s
    </ul>

%s""" % (
        T("span", "How I can help", "Cómo puedo ayudar", key="services.h1"),
        T("p", "I work with oil and gas operators and service companies. These are the areas where I can add the most.",
          "Trabajo con operadoras y empresas de servicios de petróleo y gas. Estas son las áreas donde más puedo aportar.", cls="lede"),
        "\n".join(rows), closing())
    return shell("services", "services",
                 ("Services | Miguel Lopez", "Servicios | Miguel Lopez"),
                 ("Drilling and remedial consulting, drilling optimization, tenders and contracts, business assessments and team development for oil and gas companies.",
                  "Consultoría en perforación y operaciones remediales, optimización de perforación, licitaciones y contratos, evaluaciones de negocio y desarrollo de equipos para empresas de petróleo y gas."),
                 main)


def page_experience():
    global PAGE
    PAGE = "experience"
    items = []
    for e in CAREER:
        yrs = years_t(e["from"], e["to"])
        name = esc(e["company"]) if e["company"] else T("span", e["company_t"][0], e["company_t"][1])
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
          <h2 class="log-company">%(name)s</h2>
%(place)s
          <ul class="log-roles">
%(roles)s
          </ul>
%(paras)s
        </div>
      </li>""" % {"c": e["c"], "id": e["id"], "yrs": T("span", yrs[0], yrs[1]), "name": name,
                   "place": place, "roles": "\n".join(roles), "paras": paras})
    main = """    <h1 class="hero-title">%s</h1>
    %s

    %s

    <ol class="log">
%s
    </ol>

%s""" % (
        T("span", "Career log", "Trayectoria", key="experience.h1"),
        T("p", "More than 37 years in oil and gas, newest first. Each block on the strip is as wide as the years spent there.",
          "Más de 37 años en petróleo y gas, de lo más reciente a lo más antiguo. Cada bloque de la franja es tan ancho como los años dedicados.", cls="lede"),
        strip("experience"), "\n".join(items), closing())
    return shell("experience", "experience",
                 ("Experience | Miguel Lopez", "Experiencia | Miguel Lopez"),
                 ("Career log of Miguel Lopez: PDVSA, Baker Hughes, Smith International, Schlumberger, Nabors, Wellbore Integrity Solutions and Roku Tech.",
                  "Trayectoria de Miguel Lopez: PDVSA, Baker Hughes, Smith International, Schlumberger, Nabors, Wellbore Integrity Solutions y Roku Tech."),
                 main)


def page_about():
    global PAGE
    PAGE = "about"
    steps = [
        ("Evaluate progress", "Evaluar el avance"),
        ("Optimize strategies", "Optimizar las estrategias"),
        ("Make decisions", "Tomar decisiones"),
        ("Measure performance", "Medir el desempeño"),
    ]
    ways = [
        ("Results-driven leadership, focused on operational efficiency and profitability.",
         "Liderazgo orientado a resultados, enfocado en la eficiencia operativa y la rentabilidad."),
        ("Strict respect for drilling and intervention procedures, and early management of risk.",
         "Respeto estricto de los procedimientos de perforación e intervención, y gestión anticipada del riesgo."),
        ("Service quality and full compliance with service level agreements.",
         "Calidad del servicio y cumplimiento total de los acuerdos de nivel de servicio."),
        ("Hands-on management of field teams from several disciplines.",
         "Gestión cercana de equipos de campo de varias disciplinas."),
        ("Financial management: profit and loss, gross margin, budgets, forecasts and cost control.",
         "Gestión financiera: pérdidas y ganancias, margen bruto, presupuestos, pronósticos y control de costos."),
        ("Failure investigation and root-cause analysis for complex technical problems.",
         "Investigación de fallas y análisis de causa raíz para problemas técnicos complejos."),
    ]
    ol = "\n".join("          <li>%s</li>" % T("span", a, b) for a, b in steps)
    ul = "\n".join("          <li>%s</li>" % T("span", a, b) for a, b in ways)
    ES["about.facts.edu"] = "Estudios"
    ES["about.facts.lang"] = "Idiomas"
    ES["about.facts.where"] = "Dónde he trabajado"
    ES["about.facts.base"] = "Con sede en"
    main = """    <h1 class="hero-title">%(h1)s</h1>

    <article class="profile" aria-labelledby="profile-name">
      <div class="profile-main">
        <h2 class="profile-name" id="profile-name">Miguel Enrique Lopez Gudiño</h2>
        %(role)s
        %(p1)s
        %(p2)s
        <ol class="steps">
%(ol)s
        </ol>
        %(p3)s
      </div>

      <dl class="facts">
        <div>
          <dt data-i18n="about.facts.edu">Education</dt>
          <dd>%(edu)s</dd>
        </div>
        <div>
          <dt data-i18n="about.facts.lang">Languages</dt>
          <dd>%(lang)s</dd>
        </div>
        <div>
          <dt data-i18n="about.facts.where">Where I have worked</dt>
          <dd>%(where)s</dd>
        </div>
        <div>
          <dt data-i18n="about.facts.base">Based in</dt>
          <dd>Bogotá, Colombia</dd>
        </div>
      </dl>
    </article>

    <section class="ways" aria-labelledby="ways-title">
      %(wt)s
      <ul class="ways-list">
%(ul)s
      </ul>
    </section>

%(closing)s""" % {
        "h1": T("span", "About me", "Sobre mí", key="about.h1"),
        "role": T("p", "Senior petroleum engineer", "Ingeniero de petróleo senior", cls="profile-role"),
        "p1": T("p", "I am a petroleum engineer with more than 37 years in oil and gas across Latin America. I started in reservoir and drilling engineering and moved on to country and regional management.",
                "Soy ingeniero de petróleo con más de 37 años en petróleo y gas en toda Latinoamérica. Comencé en ingeniería de yacimientos y de perforación, y pasé después a la gerencia de país y regional."),
        "p2": T("p", "I like to work from data and numbers. My method has four steps:",
                "Me gusta trabajar con datos y cifras. Mi método tiene cuatro pasos:"),
        "ol": ol,
        "p3": T("p", "I have managed operations, contracts and tenders in several countries for global service companies such as Schlumberger, Nabors and Baker Hughes.",
                "He dirigido operaciones, contratos y licitaciones en varios países para empresas globales de servicios como Schlumberger, Nabors y Baker Hughes."),
        "edu": T("span", "Bachelor's degree in Petroleum Engineering, Universidad del Zulia, Venezuela, 1982 to 1989.",
                 "Ingeniero de Petróleo, Universidad del Zulia, Venezuela, 1982 a 1989."),
        "lang": T("span", "English and Spanish, fluent. Portuguese, intermediate.",
                  "Inglés y español, con fluidez. Portugués, nivel intermedio."),
        "where": T("span", "Venezuela, Colombia, Ecuador, Peru, Brazil, Argentina, Bolivia, Trinidad and Tobago, Mexico and Central America.",
                   "Venezuela, Colombia, Ecuador, Perú, Brasil, Argentina, Bolivia, Trinidad y Tobago, México y Centroamérica."),
        "wt": T("h2", "How I work", "Cómo trabajo", cls="ways-title", extra='id="ways-title"'),
        "ul": ul,
        "closing": closing(),
    }
    return shell("about", "about",
                 ("About | Miguel Lopez", "Sobre mí | Miguel Lopez"),
                 ("About Miguel Lopez: petroleum engineer, 37 years in oil and gas across Latin America, languages and way of working.",
                  "Sobre Miguel Lopez: ingeniero de petróleo, 37 años en petróleo y gas en Latinoamérica, idiomas y forma de trabajar."),
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
    </p>""" % (
        T("h1", "This page does not exist", "Esta página no existe", cls="hero-title"),
        T("p", "The link may be out of date or mistyped. Try one of these instead.",
          "Es posible que el enlace esté desactualizado o mal escrito. Pruebe con uno de estos.", cls="lede lede--after"))
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
