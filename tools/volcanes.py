# Baja el informe semanal de actividad volcánica (Smithsonian / USGS) y lo deja en volcanes.json,
# que la app lee desde su propio sitio (la fuente original no permite lectura directa desde el navegador).
import json, re, html, datetime

URL = "https://volcano.si.edu/news/WeeklyVolcanoRSS.xml"
TIPO = {"New Eruptive Activity": "Nueva actividad eruptiva", "Continuing Eruptive Activity": "Actividad eruptiva continua",
        "Other Observations": "Otras observaciones", "New Unrest": "Nueva inquietud", "Continuing Unrest": "Inquietud continua"}
PAIS = {"Chile": "Chile", "Argentina": "Argentina", "Chile-Argentina": "Chile-Argentina", "Peru": "Perú", "Bolivia": "Bolivia",
        "Ecuador": "Ecuador", "Colombia": "Colombia", "Mexico": "México", "Guatemala": "Guatemala", "Nicaragua": "Nicaragua",
        "Costa Rica": "Costa Rica", "El Salvador": "El Salvador", "United States": "EE.UU.", "Italy": "Italia", "Japan": "Japón",
        "Indonesia": "Indonesia", "Philippines": "Filipinas", "Russia": "Rusia", "Iceland": "Islandia", "Vanuatu": "Vanuatu",
        "Papua New Guinea": "Papúa Nueva Guinea", "New Zealand": "Nueva Zelanda", "Antarctica": "Antártica"}

import sys
xml = open(sys.argv[1], encoding="iso-8859-1").read()  # lo descarga curl en el workflow (urllib recibe 403)
out = []
for it in xml.split("<item>")[1:]:
    t = html.unescape(re.search(r"<title>(.*?)</title>", it, re.S).group(1)).strip()
    m = re.match(r"(.+?) \((.+?)\) - Report for (.+?) - (.+)", t)
    if not m:
        continue
    desc = re.search(r"<description>(.*?)</description>", it, re.S)
    texto = re.sub(r"<[^>]+>", " ", html.unescape(desc.group(1) if desc else ""))
    texto = re.sub(r"\s+", " ", texto.split("Source")[0]).strip()
    link = re.search(r"<link>(.*?)</link>", it, re.S)
    pt = re.search(r"<georss:point>\s*([-\d.]+)\s+([-\d.]+)", it)
    out.append({"nombre": m.group(1), "pais": PAIS.get(m.group(2), m.group(2)), "periodo": m.group(3),
                "tipo": TIPO.get(m.group(4).strip(), m.group(4).strip()), "texto": texto[:600],
                "link": link.group(1).strip() if link else "https://volcano.si.edu/reports_weekly.cfm",
                "lat": float(pt.group(1)) if pt else None, "lon": float(pt.group(2)) if pt else None})
json.dump({"fuente": "Smithsonian Institution / USGS — Weekly Volcanic Activity Report", "actualizado": datetime.date.today().isoformat(),
           "volcanes": out}, open("volcanes.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "volcanes")
