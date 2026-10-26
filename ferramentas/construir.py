# Monta o site da Bunyy Wiki a partir da pasta "conteudo".
# Uso (na raiz do repositório):  python ferramentas/construir.py
# Resultado: pasta "_site", pronta para o GitHub Pages.
import os, re, json, html, glob, shutil, base64, unicodedata
import yaml, markdown

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(RAIZ, "conteudo")
SAIDA = os.path.join(RAIZ, "_site")
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ORDEM_GRUPOS = ["Personagens", "Grupos", "Capítulos", "Lugares", "Conceitos", "Criaturas", "Sobre"]
ORDEM_SECOES = ["Aparência", "Poderes e luta", "Gostos e personalidade", "Família e passado", "Na história e outros"]

def ler_yaml(nome):
    with open(os.path.join(C, nome), encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def slug(t):
    t = unicodedata.normalize("NFD", str(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def img(p):
    return (p or "").lstrip("/")

# ---------- capítulos ----------
CAP = ler_yaml("capitulos.yml")
HQ = sorted(CAP.get("hq") or [], key=lambda c: c["numero"])
NOVEL = sorted(CAP.get("novel") or [], key=lambda c: c["numero"])
NOVEL_T = {c["numero"]: (c.get("titulo") or "") for c in NOVEL}
def captitle(n):
    n = int(n); t = NOVEL_T.get(n, "")
    return f"Capítulo {n}: {t}" if t else f"Capítulo {n}"

# ---------- markdown ----------
def chips(s):
    s = re.sub(r"\\?\{cap (\d+)\\?\}", lambda m: f'<a class="cap" href="#capitulo-{m.group(1)}" title="Novel, {html.escape(captitle(m.group(1)))}">cap.&nbsp;{m.group(1)}</a>', s)
    s = re.sub(r"\\?\{hq (\d+)\\?\}", lambda m: f'<a class="cap hqcap" href="https://fliptru.com.br/comic/bunyy/{int(m.group(1)):03d}" target="_blank" rel="noopener" title="HQ, capítulo {m.group(1)}">HQ&nbsp;{m.group(1)}</a>', s)
    return s

SLUGS = set()
def links(s):
    def interno(m):
        alvo = m.group(2)
        if alvo in SLUGS: return f'<a href="#{alvo}">{m.group(3)}</a>'
        return m.group(3)
    s = re.sub(r'<a href="#([a-z0-9-]+)">(.*?)</a>', lambda m: m.group(0) if m.group(1) in SLUGS or m.group(1) in TABS else m.group(2), s)
    s = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank" rel="noopener">', s)
    return s
TABS = {"inicio", "hq-e-novel", "curiosidades", "personagens", "lugares", "o-mundo", "grupos", "criaturas", "mapa"}

def md(texto, inline=False):
    h = markdown.markdown(texto or "", extensions=["tables", "sane_lists"])
    if inline: h = re.sub(r"^<p>(.*)</p>$", r"\1", h.strip(), flags=re.S)
    h = links(chips(h))
    h = re.sub(r"<(h[23])>(.*?)</\1>", lambda m: f'<{m.group(1)} id="{slug(re.sub("<[^>]+>", "", m.group(2)))}">{m.group(2)}</{m.group(1)}>', h)
    h = h.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    return h

def plain(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()

# ---------- falas do Toom ----------
def dchip(it, curto=False):
    if not it.get("link"):
        return '<span class="cap dccap" title="Trecho anotado pela comunidade">roteiro</span>'
    d = str(it.get("data") or "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", d)
    lab = f"{MES[int(m.group(2)) - 1]}/{m.group(1)[2:]}" if m else "link"
    tip = f"Mensagem do Toom no Discord, {m.group(3)}/{m.group(2)}/{m.group(1)}" if m else "Mensagem do Toom no Discord"
    return f'<a class="cap dccap" href="{html.escape(it["link"])}" target="_blank" rel="noopener" title="{tip}">{"" if curto else "Discord · "}{lab}</a>'

AVISO = ('<p class="src-note">Falas do Toom no servidor oficial do Discord, por data. Ele às vezes brinca ou muda de ideia: '
         'na dúvida, vale a fala mais recente e, acima de tudo, o que está na obra. A data ao lado de cada frase abre a mensagem original.</p>')

def secao_falas(fm):
    itens = [i for i in (fm.get("segundo_o_toom") or []) if i and i.get("texto")]
    if not itens: return ""
    itens.sort(key=lambda i: str(i.get("data") or ""))
    titulo = fm.get("titulo_falas") or "Segundo o Toom (Discord)"
    secoes = []
    for i in itens:
        s = (i.get("secao") or "").strip()
        if s not in secoes: secoes.append(s)
    li = lambda i, curto: f"<li>{md(i['texto'], inline=True)}{dchip(i, curto)}</li>"
    if secoes == [""]:
        return f'<h2 id="segundo-o-toom">{html.escape(titulo)}</h2>' + AVISO + '<ul class="dc-list">' + "".join(li(i, False) for i in itens) + "</ul>"
    secoes.sort(key=lambda s: ORDEM_SECOES.index(s) if s in ORDEM_SECOES else 50)
    if fm.get("secoes_como_titulos"):
        out = ""
        for k, s in enumerate(secoes):
            out += f'<h2 id="{slug(s) or "outros"}">{html.escape(s or "Outros")}</h2>' + (AVISO if k == 0 else "")
            out += '<ul class="dc-list">' + "".join(li(i, False) for i in itens if (i.get("secao") or "").strip() == s) + "</ul>"
        return out
    out = f'<h2 id="segundo-o-toom">{html.escape(titulo)}</h2>' + AVISO
    for s in secoes:
        grupo = [i for i in itens if (i.get("secao") or "").strip() == s]
        out += f'<h3 class="dc-h">{html.escape(s or "Outros")} <small>{len(grupo)}</small></h3><ul class="dc-list">' + "".join(li(i, True) for i in grupo) + "</ul>"
    return out

# ---------- páginas ----------
def ler_pagina(caminho):
    txt = open(caminho, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", txt, re.S)
    fm, corpo = (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, txt)
    return fm, corpo

arquivos = sorted(glob.glob(os.path.join(C, "paginas", "*.md")))
brutas = []
for a in arquivos:
    fm, corpo = ler_pagina(a)
    if not fm.get("titulo"): continue
    s_ = os.path.splitext(os.path.basename(a))[0]
    SLUGS.add(s_); brutas.append((s_, fm, corpo))

pages, curios, acurios, dcurios = [], [], [], []
CFG = {"paginas": {}, "capas_hq": {}, "novel": {}}
for s_, fm, corpo in brutas:
    h = ""
    ficha = [f for f in (fm.get("ficha") or []) if f and f.get("campo")]
    if ficha:
        linhas = "".join(f'<div class="ib-row"><dt>{html.escape(str(f["campo"]))}</dt><dd>{md(str(f.get("valor") or ""), inline=True)}</dd></div>' for f in ficha)
        h += f'<aside class="infobox" aria-label="Ficha"><div class="ib-name">{html.escape(str(fm.get("ficha_nome") or fm["titulo"]))}</div><dl>{linhas}</dl></aside>\n'
    h += md(corpo)
    m = re.match(r"capitulo-(\d+)$", s_)
    if m:
        n = int(m.group(1)); ns = [c["numero"] for c in NOVEL]
        ant = max([x for x in ns if x < n], default=None); prox = min([x for x in ns if x > n], default=None)
        h += '<nav class="chapnav">' + (f'<a href="#capitulo-{ant}">← {html.escape(captitle(ant))}</a>' if ant else "<span></span>") + \
             (f'<a href="#capitulo-{prox}">{html.escape(captitle(prox))} →</a>' if prox else "<span></span>") + "</nav>"
    ex = [e for e in (fm.get("extras_do_autor") or []) if e and e.get("texto")]
    if ex:
        itens = [md(e["texto"], inline=True) + chips(f'{{hq {int(e["hq"])}}}' if e.get("hq") else "") for e in ex]
        h += '<h2 id="extras-do-autor">Extras do autor</h2><p class="src-note">Informações das páginas extras publicadas pelo Toom no fim dos capítulos da HQ.</p><ul>' + "".join(f"<li>{i}</li>" for i in itens) + "</ul>"
        acurios.append({"s": s_, "t": fm["titulo"], "items": itens})
    h += secao_falas(fm)
    for i in (fm.get("segundo_o_toom") or []):
        if i and i.get("destaque") and i.get("texto"):
            dcurios.append({"s": s_, "h": f"<li><b>{html.escape(fm['titulo'])}:</b> {md(i['texto'], inline=True)}{dchip(i)}</li>", "d": str(i.get("data") or "")})
    fal = [q for q in (fm.get("falas_marcantes") or []) if q and q.get("fala")]
    if fal:
        h += '<h2 id="falas-marcantes">Falas marcantes</h2><div class="balloons">'
        for q in fal:
            c = q.get("capitulo")
            h += (f'<figure class="balloon"><blockquote>{html.escape(str(q["fala"]))}</blockquote><figcaption>{html.escape(str(q.get("contexto") or ""))}'
                  + (chips(f"{{cap {int(c)}}}") if c else "") + "</figcaption></figure>")
        h += "</div>"
    cm = re.search(r'<h2 id="curiosidades">Curiosidades</h2>\s*<ul>(.*?)</ul>', h, re.S)
    if cm: curios.append({"s": s_, "t": fm["titulo"], "items": re.findall(r"<li>(.*?)</li>", cm.group(1), re.S)})
    fonte = {"obra": "novel", "discord": "discord"}.get(fm.get("fonte") or "", "")
    pages.append({"s": s_, "t": fm["titulo"], "g": fm.get("grupo") or "Sobre", "sub": fm.get("subtitulo") or "", "sp": fm.get("spoiler_ate") or None,
                  "f": fonte or None, "lado": fm.get("lado") or "", "curto": fm.get("nome_curto") or "", "o": fm.get("ordem") or 999, "tipo": fm.get("tipo_criatura") or "",
                  "h": h, "x": plain(h)[:12000]})
    e = {}
    if fm.get("foto"): e["foto"], e["legenda"] = img(fm["foto"]), fm.get("foto_legenda") or ""
    if fm.get("imagem_card"): e["card"] = img(fm["imagem_card"])
    gal = [{"arquivo": img(g["imagem"]), "legenda": g.get("legenda") or ""} for g in (fm.get("galeria") or []) if g and g.get("imagem")]
    ver = [{"arquivo": img(g["imagem"]), "legenda": g.get("legenda") or ""} for g in (fm.get("versoes") or []) if g and g.get("imagem")]
    if gal: e["galeria"] = gal
    if ver: e["versoes"] = ver
    if e: CFG["paginas"][s_] = e

# capítulos sem imagem própria usam a capa da HQ
for c in NOVEL:
    s_ = f"capitulo-{c['numero']}"
    hs = c.get("capitulos_da_hq") or []
    capas = [x for x in HQ if x["numero"] in hs and x.get("capa")]
    if s_ in SLUGS and capas and not CFG["paginas"].get(s_, {}).get("foto"):
        CFG["paginas"].setdefault(s_, {})
        CFG["paginas"][s_]["foto"] = img(capas[0]["capa"])
        CFG["paginas"][s_]["legenda"] = f'Capa da HQ, capítulo {capas[0]["numero"]}: {capas[0]["titulo"]}'
        if len(capas) > 1 and not CFG["paginas"][s_].get("galeria"):
            CFG["paginas"][s_]["galeria"] = [{"arquivo": img(x["capa"]), "legenda": f'Capa da HQ, capítulo {x["numero"]}: {x["titulo"]}'} for x in capas[1:]]

def chave(p):
    g = ORDEM_GRUPOS.index(p["g"]) if p["g"] in ORDEM_GRUPOS else len(ORDEM_GRUPOS)
    m = re.match(r"capitulo-(\d+)$", p["s"])
    return (g, int(m.group(1)) if m else 0, p["o"], p["t"])
pages.sort(key=chave)

for c in HQ:
    if c.get("capa"): CFG["capas_hq"][str(c["numero"])] = img(c["capa"])
for c in NOVEL:
    CFG["novel"][str(c["numero"])] = c.get("link") or ""

ini = ler_yaml("inicio.yml")
ini["destaque_imagem"] = img(ini.get("destaque_imagem"))
ini["fatos"] = [md(f["texto"], inline=True) for f in (ini.get("fatos") or []) if f and f.get("texto")]
ini["novidades"] = [n for n in (ini.get("novidades") or []) if n and n.get("texto")]
mapa = ler_yaml("mapa.yml")
dcurios.sort(key=lambda d: d["d"])

DATA = {"pages": pages, "order": ORDEM_GRUPOS, "curios": curios, "config": CFG,
        "hq": [{"n": c["numero"], "t": c.get("titulo") or "", "c": c.get("classificacao") or "",
                "nv": [v["numero"] for v in NOVEL if c["numero"] in (v.get("capitulos_da_hq") or [])]} for c in HQ],
        "novel": [{"n": c["numero"], "t": c.get("titulo") or "", "hq": c.get("capitulos_da_hq") or []} for c in NOVEL],
        "acurios": acurios, "dcurios": [{"s": d["s"], "h": d["h"]} for d in dcurios], "inicio": ini, "mapa": mapa}

payload = json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")
F = os.path.join(RAIZ, "ferramentas")
tpl = open(os.path.join(F, "modelo.html"), encoding="utf-8").read()
fonte64 = base64.b64encode(open(os.path.join(F, "warning-sub.woff2"), "rb").read()).decode()
pagina = tpl.replace("/*__DATA__*/null", payload).replace("/*__WARNING__*/", fonte64)
completo = ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + pagina.replace("<!--HEAD-END-->", "</head>\n<body>", 1) + "\n</body>\n</html>\n")

if os.path.exists(SAIDA): shutil.rmtree(SAIDA)
os.makedirs(SAIDA)
open(os.path.join(SAIDA, "index.html"), "w", encoding="utf-8").write(completo)
open(os.path.join(SAIDA, "artifact.html"), "w", encoding="utf-8").write(pagina)
if os.path.isdir(os.path.join(RAIZ, "imagens")):
    shutil.copytree(os.path.join(RAIZ, "imagens"), os.path.join(SAIDA, "imagens"))
open(os.path.join(SAIDA, ".nojekyll"), "w").close()
print(f"Site montado: {len(pages)} páginas, {len(completo) // 1024} KB")
